import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const TOTAL = 200;
const COLS = 20;

/** SC-12 (1:30-1:42): one wireframe document duplicates, fanning out into 200. Match-cut in. */
export const SC12: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const durationInFrames = 12 * fps;

  const fanProgress = interpolate(frame, [10, durationInFrames - 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const cellW = width * 0.86 / COLS;
  const rows = Math.ceil(TOTAL / COLS);
  const cellH = cellW * 1.3;
  const gridW = cellW * COLS;
  const gridH = cellH * rows;
  const gridLeft = width / 2 - gridW / 2;
  const gridTop = height / 2 - gridH / 2;
  const centerX = width / 2;
  const centerY = height / 2;
  const singleW = 180;
  const singleH = singleW * 1.3;

  return (
    <SceneShell>
      <AbsoluteFill>
        {Array.from({ length: TOTAL }).map((_, i) => {
          const row = Math.floor(i / COLS);
          const col = i % COLS;
          const targetX = gridLeft + col * cellW;
          const targetY = gridTop + row * cellH;
          const targetW = cellW - 4;
          const targetH = cellH - 4;

          const x = interpolate(fanProgress, [0, 1], [centerX - singleW / 2, targetX]);
          const y = interpolate(fanProgress, [0, 1], [centerY - singleH / 2, targetY]);
          const w = interpolate(fanProgress, [0, 1], [singleW, targetW]);
          const h = interpolate(fanProgress, [0, 1], [singleH, targetH]);
          const opacity = i === 0 ? 1 : interpolate(fanProgress, [0, 0.15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: x,
                top: y,
                width: w,
                height: h,
                border: `2px solid ${COLORS.text}`,
                opacity,
                borderRadius: 2,
              }}
            />
          );
        })}
      </AbsoluteFill>
    </SceneShell>
  );
};
