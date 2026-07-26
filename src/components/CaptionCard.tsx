import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../constants/theme";
import { Aspect } from "../types";
import { useSceneLayout } from "../utils/layout";

// The VO script spells numbers out for TTS pronunciation ("two hundred and
// fifty thousand"), so the "number" caption rule needs to catch cardinal
// number words too, not just literal digits.
const NUMBER_WORDS = new Set([
  "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
  "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
  "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
  "hundred", "thousand", "million", "billion", "point", "percent",
]);

const isNumberWord = (word: string) => {
  const stripped = word.toLowerCase().replace(/[^a-z0-9-]/g, "");
  if (/\d/.test(stripped)) return true;
  return stripped.split("-").some((part) => NUMBER_WORDS.has(part));
};

export type CaptionWord = {
  text: string;
  /** Frame (relative to the enclosing Sequence) this word becomes active. */
  startFrame: number;
};

type Props = {
  /** Max 4 words per card, per the caption spec. */
  words: CaptionWord[];
  aspect: Aspect;
};

/**
 * Burned-in bottom-third caption. Words reveal one at a time on their
 * startFrame; a word containing a digit is highlighted flagged-red while
 * active, per the caption spec ("number words only").
 */
export const CaptionCard: React.FC<Props> = ({ words, aspect }) => {
  const frame = useCurrentFrame();
  const { height } = useVideoConfig();
  const { safeWidth, fontScale, isVertical } = useSceneLayout(aspect);
  const fontSize = 44 * fontScale;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        bottom: isVertical ? height * 0.16 : height * 0.12,
        transform: "translateX(-50%)",
        width: safeWidth,
        display: "flex",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: "0.35em",
      }}
    >
      {words.map((w, i) => {
        const revealed = frame >= w.startFrame;
        const opacity = interpolate(frame, [w.startFrame, w.startFrame + 6], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const isNumber = isNumberWord(w.text);
        const active = revealed && frame < w.startFrame + 18;
        return (
          <span
            key={i}
            style={{
              opacity: revealed ? opacity : 0,
              fontFamily: FONTS.body,
              fontWeight: 800,
              fontSize,
              color: isNumber && active ? COLORS.flagged : COLORS.text,
              textShadow: "0 2px 12px rgba(0,0,0,0.65)",
              textTransform: "uppercase",
              letterSpacing: "0.01em",
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
