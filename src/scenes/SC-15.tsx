import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { DonutStat } from "../components/DonutStat";
import { COLORS } from "../constants/theme";
import { assertLabeledDualColor } from "../constants/colorRule";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/** SC-15 (2:06-2:14): two donuts fill simultaneously — 91% accuracy (teal), 9.87% flagged (red). Labeled per the color rule. */
export const SC15: React.FC<SceneProps> = ({ aspect }) => {
  assertLabeledDualColor(true, true); // both donuts carry a text label
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { fontScale, isVertical } = useSceneLayout(aspect);
  const durationInFrames = 8 * fps;

  const progress = interpolate(frame, [8, durationInFrames - 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <SceneShell>
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          flexDirection: isVertical ? "column" : "row",
          gap: isVertical ? 60 : 160,
        }}
      >
        <DonutStat percent={91} progress={progress} color={COLORS.legit} label="ACCURACY (TEST)" fontScale={fontScale} />
        <DonutStat percent={9.87} progress={progress} color={COLORS.flagged} label="FLAGGED" fontScale={fontScale} />
      </AbsoluteFill>
    </SceneShell>
  );
};
