import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const RUNG_SPACING = 46;
const CLIMB_RUNGS_PER_SEC = 0.7;
const LADDER_RUNGS_PER_SEC = 2.1;

/**
 * SC-08 (0:52-1:04): a paper-rung career ladder multiplies downward faster
 * than the figure climbing it can keep pace — the sympathy beat. Never cut
 * for time. A 2-curve supply/demand chart appears briefly (<2s).
 */
export const SC08: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { height, fontScale } = useSceneLayout(aspect);
  const t = frame / fps;

  const rungCount = Math.min(40, 6 + Math.floor(t * LADDER_RUNGS_PER_SEC));
  const climberRung = t * CLIMB_RUNGS_PER_SEC;

  const chartStart = 6.5 * fps;
  const chartOpacity = interpolate(
    frame,
    [chartStart, chartStart + 6, chartStart + 6 + 1.6 * fps, chartStart + 6 + 1.6 * fps + 10],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center" }}>
        <div style={{ position: "relative", width: 220, height: height * 0.9 }}>
          <div
            style={{
              position: "absolute",
              left: 30,
              bottom: 0,
              width: 6,
              height: rungCount * RUNG_SPACING,
              background: COLORS.uncertain,
              opacity: 0.5,
            }}
          />
          <div
            style={{
              position: "absolute",
              right: 30,
              bottom: 0,
              width: 6,
              height: rungCount * RUNG_SPACING,
              background: COLORS.uncertain,
              opacity: 0.5,
            }}
          />
          {Array.from({ length: rungCount }).map((_, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: 24,
                bottom: i * RUNG_SPACING,
                width: 172,
                height: 10,
                background: COLORS.uncertain,
                borderRadius: 2,
              }}
            />
          ))}
          <div
            style={{
              position: "absolute",
              left: 88,
              bottom: climberRung * RUNG_SPACING,
              width: 44,
              height: 44,
              borderRadius: "50%",
              background: COLORS.text,
            }}
          />
        </div>
      </AbsoluteFill>

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start" }}>
        <div
          style={{
            marginTop: height * 0.1,
            opacity: chartOpacity,
            background: "#0F1424",
            border: "1px solid #2C3448",
            borderRadius: 10,
            padding: 20,
          }}
        >
          <svg width={260} height={160} viewBox="0 0 260 160">
            <path d="M10,150 L250,20" stroke={COLORS.uncertain} strokeWidth={4} fill="none" />
            <path d="M10,20 L250,150" stroke={COLORS.text} strokeWidth={4} fill="none" opacity={0.7} />
            <text x="150" y="15" fill={COLORS.uncertain} fontFamily={FONTS.body} fontSize={14 * fontScale}>
              SUPPLY
            </text>
            <text x="10" y="35" fill={COLORS.text} fontFamily={FONTS.body} fontSize={14 * fontScale} opacity={0.7}>
              DEMAND
            </text>
          </svg>
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
