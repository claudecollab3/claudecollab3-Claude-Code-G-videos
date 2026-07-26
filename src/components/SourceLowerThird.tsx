import React from "react";
import { useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../constants/theme";
import { Aspect } from "../types";

type Props = {
  source: string; // e.g. "The BMJ"
  year: string | number; // e.g. 2026
  aspect: Aspect;
};

/** Static, 60%-opacity source credit. No animation, per spec — appears for 2.5s via the parent Sequence's duration. */
export const SourceLowerThird: React.FC<Props> = ({ source, year, aspect }) => {
  const { height } = useVideoConfig();
  const isVertical = aspect === "vertical";
  return (
    <div
      style={{
        position: "absolute",
        left: isVertical ? 48 : 64,
        bottom: isVertical ? height * 0.28 : 56,
        opacity: 0.6,
        fontFamily: FONTS.body,
        fontWeight: 600,
        fontSize: isVertical ? 30 : 22,
        color: COLORS.text,
        letterSpacing: "0.02em",
      }}
    >
      {source} · {year}
    </div>
  );
};
