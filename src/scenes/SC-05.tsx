import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

// Shared bar pattern (widths as fraction of block width) — identical across
// all six blocks, standing in for "the same sentence shapes" without ever
// rendering legible text.
const BAR_PATTERN = [0.9, 0.6, 0.75, 0.4, 0.85];

const EDGES: { from: { x: number; y: number }; to: { x: number; y: number } }[] = [
  { from: { x: 0, y: -1.4 }, to: { x: 0, y: 0 } }, // top
  { from: { x: 0, y: 1.4 }, to: { x: 0, y: 0 } }, // bottom
  { from: { x: -1.6, y: 0 }, to: { x: 0, y: 0 } }, // left
  { from: { x: 1.6, y: 0 }, to: { x: 0, y: 0 } }, // right
  { from: { x: -1.4, y: -1.1 }, to: { x: 0, y: 0 } }, // top-left
  { from: { x: 1.4, y: 1.1 }, to: { x: 0, y: 0 } }, // bottom-right
];

const BLOCK_POSITIONS = [
  { col: 0, row: 0 },
  { col: 1, row: 0 },
  { col: 2, row: 0 },
  { col: 0, row: 1 },
  { col: 1, row: 1 },
  { col: 2, row: 1 },
];

export const SC05: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const durationInFrames = 12 * fps;

  const blockW = width * 0.24;
  const blockH = height * 0.22;
  const gridW = blockW * 3 + 40 * 2;
  const gridH = blockH * 2 + 40;
  const gridLeft = width / 2 - gridW / 2;
  const gridTop = height / 2 - gridH / 2;

  const arriveEnd = 24; // frames each block takes to slide/align, staggered
  const staggerPerBlock = 4;

  const whipStart = durationInFrames - 8;
  const whipProgress = interpolate(frame, [whipStart, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  return (
    <SceneShell>
      <AbsoluteFill
        style={{
          transform: `translateX(${whipProgress * width * 1.4}px) scaleX(${1 + whipProgress * 2})`,
          filter: whipProgress > 0 ? `blur(${whipProgress * 18}px)` : undefined,
        }}
      >
        {BLOCK_POSITIONS.map((pos, i) => {
          const startFrame = i * staggerPerBlock;
          const arriveProgress = interpolate(frame, [startFrame, startFrame + arriveEnd], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          const edge = EDGES[i];
          const dx = interpolate(arriveProgress, [0, 1], [edge.from.x, edge.to.x]) * blockW;
          const dy = interpolate(arriveProgress, [0, 1], [edge.from.y, edge.to.y]) * blockH;
          const left = gridLeft + pos.col * (blockW + 40);
          const top = gridTop + pos.row * (blockH + 40);

          // All six blocks illuminate the same bar index at the same time,
          // sweeping through the pattern — the recurring "fingerprint".
          const illuminateStart = arriveEnd + 6;
          const barCycle = 10;
          const activeBar = Math.floor((frame - illuminateStart) / barCycle);

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left,
                top,
                width: blockW,
                height: blockH,
                background: "#171D2E",
                border: "1px solid #2C3448",
                borderRadius: 6,
                opacity: arriveProgress,
                transform: `translate(${dx}px, ${dy}px)`,
                padding: 18,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                gap: 10,
              }}
            >
              {BAR_PATTERN.map((w, barI) => (
                <div
                  key={barI}
                  style={{
                    height: 8,
                    width: `${w * 100}%`,
                    borderRadius: 3,
                    background: barI === activeBar ? COLORS.legit : "#3A4358",
                    boxShadow: barI === activeBar ? `0 0 14px 2px ${COLORS.legit}` : undefined,
                  }}
                />
              ))}
            </div>
          );
        })}
      </AbsoluteFill>
    </SceneShell>
  );
};
