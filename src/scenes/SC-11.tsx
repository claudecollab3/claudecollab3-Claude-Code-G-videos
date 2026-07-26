import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-11 (1:24-1:30): the 90-second re-hook. A tiny human silhouette at the
 * base of the SC-01 column; a continuous 4s crane up while the column never
 * ends. The longest unbroken camera move in the video — do not shorten.
 */
export const SC11: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const durationInFrames = 6 * fps;
  const craneStart = durationInFrames - 4 * fps;

  const craneProgress = interpolate(frame, [craneStart, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const scrollY = craneProgress * height * 6;

  return (
    <SceneShell>
      <AbsoluteFill>
        <PaperColumn count={220} scrollY={scrollY} width={width} height={height} spread={0.1} />
      </AbsoluteFill>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 40 }}>
        <div
          style={{
            opacity: interpolate(craneProgress, [0, 0.3], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            width: 26,
            height: 60,
            borderRadius: "10px 10px 0 0",
            background: COLORS.uncertain,
          }}
        />
      </AbsoluteFill>
    </SceneShell>
  );
};
