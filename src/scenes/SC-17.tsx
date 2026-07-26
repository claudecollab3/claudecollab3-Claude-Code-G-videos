import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { LineChartReveal } from "../components/LineChartReveal";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const TIERS = 6;

const Pyramid: React.FC<{ frame: number; width: number; height: number; fontScale: number }> = ({ frame, width, height, fontScale }) => {
  const pyramidWidth = Math.min(width * 0.5, 520);
  const pyramidHeight = height * 0.5;
  const tierH = pyramidHeight / TIERS;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 20 }}>
      <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 24 * fontScale, color: COLORS.text, opacity: 0.8 }}>
        JOURNAL PRESTIGE TIERS
      </div>
      <svg width={pyramidWidth} height={pyramidHeight} viewBox={`0 0 ${pyramidWidth} ${pyramidHeight}`}>
        {Array.from({ length: TIERS }).map((_, i) => {
          const tierFromBase = TIERS - 1 - i;
          const topFrac = i / TIERS;
          const bottomFrac = (i + 1) / TIERS;
          const topW = pyramidWidth * topFrac;
          const bottomW = pyramidWidth * bottomFrac;
          const y = i * tierH;
          const points = `${pyramidWidth / 2 - topW / 2},${y} ${pyramidWidth / 2 + topW / 2},${y} ${pyramidWidth / 2 + bottomW / 2},${y + tierH} ${pyramidWidth / 2 - bottomW / 2},${y + tierH}`;
          const creepStart = 12 + tierFromBase * 10;
          const fillProgress = interpolate(frame, [creepStart, creepStart + 8], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <polygon
              key={i}
              points={points}
              fill={fillProgress > 0.5 ? COLORS.flagged : "#232B40"}
              stroke="#0A0E1A"
              strokeWidth={2}
              opacity={0.9}
            />
          );
        })}
      </svg>
      <div style={{ fontFamily: FONTS.body, fontSize: 18 * fontScale, color: COLORS.uncertain, opacity: 0.85 }}>
        APEX = TOP 10% BY IMPACT FACTOR
      </div>
    </AbsoluteFill>
  );
};

/** SC-17 (2:24-2:34): red creeps up the journal-tier pyramid, then a D1 line joins the SC-16 chart. */
export const SC17: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale, isVertical } = useSceneLayout(aspect);
  const switchFrame = 5 * fps;

  const chartW = isVertical ? width * 0.92 : width * 0.62;
  const chartH = isVertical ? height * 0.34 : height * 0.5;

  if (frame < switchFrame) {
    return (
      <SceneShell>
        <Pyramid frame={frame} width={width} height={height} fontScale={fontScale} />
      </SceneShell>
    );
  }

  const localFrame = frame - switchFrame;
  const progress = interpolate(localFrame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 16 }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 22 * fontScale, color: COLORS.uncertain, letterSpacing: "0.04em" }}>
          D1 · TOP DECILE JOURNALS
        </div>
        <div style={{ opacity: progress }}>
          <LineChartReveal width={chartW} height={chartH} progress={1} showTopDecile fontScale={fontScale} />
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
