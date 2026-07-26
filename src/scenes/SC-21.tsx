import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { ScatterChart, Scatter, XAxis, YAxis } from "recharts";
import { SceneShell } from "../components/SceneShell";
import { COLORS, FONTS } from "../constants/theme";
import { seededRandom } from "../utils/seededRandom";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const messyRand = seededRandom(7);
const MESSY_DATA = Array.from({ length: 40 }).map((_, i) => ({
  x: i,
  y: 30 + Math.sin(i / 3) * 12 + (messyRand() - 0.5) * 26,
}));
const CLEAN_DATA = Array.from({ length: 40 }).map((_, i) => ({ x: i, y: 8 + i * 1.05 }));

/**
 * SC-21 (3:14-3:30): messy real data vs suspiciously clean data, then a
 * building rises with red foundation blocks. The only real-footage insert
 * (1.5s microscope clip) is a TODO — no stock source was provided.
 */
export const SC21: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale, isVertical } = useSceneLayout(aspect);
  const switchFrame = 8 * fps;

  const chartW = isVertical ? width * 0.42 : width * 0.32;
  const chartH = isVertical ? height * 0.22 : height * 0.4;

  if (frame < switchFrame) {
    const revealProgress = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <SceneShell>
        <AbsoluteFill
          style={{
            alignItems: "center",
            justifyContent: "center",
            flexDirection: isVertical ? "column" : "row",
            gap: 40,
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: revealProgress }}>
            <ScatterChart width={chartW} height={chartH}>
              <XAxis dataKey="x" hide />
              <YAxis dataKey="y" hide domain={[0, 60]} />
              <Scatter data={MESSY_DATA} fill={COLORS.legit} isAnimationActive={false} />
            </ScatterChart>
            <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 20 * fontScale, color: COLORS.legit }}>REAL DATA</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: revealProgress }}>
            <ScatterChart width={chartW} height={chartH}>
              <XAxis dataKey="x" hide />
              <YAxis dataKey="y" hide domain={[0, 60]} />
              <Scatter data={CLEAN_DATA} fill={COLORS.flagged} isAnimationActive={false} />
            </ScatterChart>
            <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 20 * fontScale, color: COLORS.flagged }}>
              SUSPICIOUSLY CLEAN
            </div>
          </div>
        </AbsoluteFill>
      </SceneShell>
    );
  }

  const localFrame = frame - switchFrame;
  const riseProgress = interpolate(localFrame, [0, 5 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tiltDown = interpolate(localFrame, [5 * fps, 7 * fps], [0, 12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const buildingH = height * 0.55 * riseProgress;
  const buildingW = width * 0.18;

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: height * 0.12, transform: `rotate(${tiltDown}deg)`, transformOrigin: "50% 80%" }}>
        <div style={{ position: "relative", width: buildingW, height: buildingH }}>
          <div style={{ position: "absolute", bottom: 0, width: "100%", height: buildingH * 0.82, background: COLORS.text }} />
          <div style={{ position: "absolute", bottom: 0, width: "100%", height: Math.min(buildingH, 40), background: COLORS.flagged }} />
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 60, opacity: riseProgress }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 24 * fontScale, color: COLORS.flagged, letterSpacing: "0.03em" }}>
          REAL TRIALS, BUILT ON A FLAGGED FOUNDATION
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
