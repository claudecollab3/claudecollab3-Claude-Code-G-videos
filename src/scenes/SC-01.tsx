import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-01 (0:00-0:03): a single sheet falls in and multiplies exponentially
 * into a column that exceeds the top of frame, while 2,600,000 counts up
 * fast under a slow 3% push-in.
 */
export const SC01: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale } = useSceneLayout(aspect);
  const durationInFrames = 3 * fps;

  // Exponential growth in sheet count, driven by frame progress.
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  const count = Math.round(1 + progress * 59); // 1 -> 60 sheets

  const scale = interpolate(frame, [0, durationInFrames], [1, 1.03], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell>
      <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: "50% 50%" }}>
        <PaperColumn count={count} scrollY={0} width={width} height={height} />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <AnimatedCounter
          to={2_600_000}
          startFrame={2}
          durationMs={2200}
          fontSize={150 * fontScale}
          color={COLORS.text}
        />
      </AbsoluteFill>
    </SceneShell>
  );
};
