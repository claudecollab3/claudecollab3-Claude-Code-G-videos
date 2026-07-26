import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { SourceLowerThird } from "../components/SourceLowerThird";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/** SC-09 (1:04-1:14): two counters race upward in parallel under a slow pull-back. */
export const SC09: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { fontScale, isVertical } = useSceneLayout(aspect);
  const durationInFrames = 10 * fps;

  const scale = interpolate(frame, [0, durationInFrames], [1.18, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const Stat: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
      {children}
      <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 26 * fontScale, color: COLORS.text, opacity: 0.8, letterSpacing: "0.03em" }}>
        {label}
      </div>
    </div>
  );

  return (
    <SceneShell>
      {frame < 75 && <SourceLowerThird source="The BMJ" year={2026} aspect={aspect} />}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${scale})`,
          flexDirection: isVertical ? "column" : "row",
          gap: isVertical ? 60 : 140,
        }}
      >
        <Stat label="SUSPECTED PAPER-MILL PAPERS, 20 YEARS">
          <AnimatedCounter to={400_000} startFrame={0} durationMs={4000} suffix="+" fontSize={110 * fontScale} color={COLORS.uncertain} />
        </Stat>
        <Stat label="ESTIMATED REVENUE / YEAR">
          <AnimatedCounter to={10} startFrame={20} durationMs={3500} prefix="$" suffix="s OF MILLIONS" fontSize={90 * fontScale} color={COLORS.uncertain} />
        </Stat>
      </AbsoluteFill>
    </SceneShell>
  );
};
