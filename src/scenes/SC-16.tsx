import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { LineChartReveal } from "../components/LineChartReveal";
import { SourceLowerThird } from "../components/SourceLowerThird";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/** SC-16 (2:14-2:24) — second most important graphic. Flagged share climbs, revealed left->right over 1.2s, camera tracks right along the line. */
export const SC16: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale, isVertical } = useSceneLayout(aspect);

  const revealFrames = 1.2 * fps;
  const progress = interpolate(frame, [0, revealFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const chartW = isVertical ? width * 0.92 : width * 0.62;
  const chartH = isVertical ? height * 0.34 : height * 0.5;

  const trackStart = revealFrames;
  const trackProgress = interpolate(frame, [trackStart, trackStart + 8 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const trackX = -trackProgress * chartW * 0.18;

  return (
    <SceneShell>
      {frame < 75 && <SourceLowerThird source="The BMJ" year={2026} aspect={aspect} />}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16 }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 24 * fontScale, color: COLORS.flagged, letterSpacing: "0.04em" }}>
          FLAGGED SHARE OF CANCER LITERATURE, 1999-2024
        </div>
        <div style={{ transform: `translateX(${trackX}px)` }}>
          <LineChartReveal width={chartW} height={chartH} progress={progress} fontScale={fontScale} />
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
