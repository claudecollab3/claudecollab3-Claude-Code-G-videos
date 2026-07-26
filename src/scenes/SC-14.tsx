import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { MotionBlurGhost } from "../components/MotionBlurGhost";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const START_YEAR = 1999;
const END_YEAR = 2024;
const TICK_YEARS = [1999, 2004, 2009, 2014, 2019, 2024];

/** SC-14 (1:54-2:06): timeline sweeps 1999->2024, a scanner line passes over the paper column. */
export const SC14: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale } = useSceneLayout(aspect);
  const durationInFrames = 12 * fps;

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const currentYear = Math.round(START_YEAR + progress * (END_YEAR - START_YEAR));

  const trackLeft = width * 0.1;
  const trackWidth = width * 0.8;
  const trackY = height * 0.86;
  const scanX = trackLeft + progress * trackWidth;
  const scanVelocity = trackWidth / durationInFrames;

  return (
    <SceneShell>
      <AbsoluteFill style={{ opacity: 0.5 }}>
        <PaperColumn count={120} scrollY={0} width={width} height={height} spread={0.09} monochrome />
      </AbsoluteFill>

      <AbsoluteFill>
        <MotionBlurGhost dx={scanVelocity}>
          <div
            style={{
              position: "absolute",
              left: scanX,
              top: 0,
              width: 3,
              height: height,
              background: COLORS.legit,
              boxShadow: `0 0 24px 4px ${COLORS.legit}`,
            }}
          />
        </MotionBlurGhost>
      </AbsoluteFill>

      <AbsoluteFill>
        <div style={{ position: "absolute", left: trackLeft, top: trackY, width: trackWidth, height: 4, background: "#2C3448" }} />
        {TICK_YEARS.map((year) => {
          const x = trackLeft + ((year - START_YEAR) / (END_YEAR - START_YEAR)) * trackWidth;
          return (
            <div key={year} style={{ position: "absolute", left: x - 20, top: trackY + 14, width: 40, textAlign: "center" }}>
              <div style={{ width: 2, height: 10, background: "#5B6478", margin: "0 auto -14px auto" }} />
              <div style={{ fontFamily: FONTS.body, fontSize: 18 * fontScale, color: COLORS.text, opacity: 0.7 }}>{year}</div>
            </div>
          );
        })}
        <div
          style={{
            position: "absolute",
            left: scanX - 60,
            top: trackY - 60,
            width: 120,
            textAlign: "center",
            fontFamily: FONTS.numeral,
            fontWeight: 700,
            fontSize: 46 * fontScale,
            color: COLORS.legit,
          }}
        >
          {currentYear}
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
