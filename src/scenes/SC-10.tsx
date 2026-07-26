import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { seededRandom } from "../utils/seededRandom";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const JOURNAL_COUNT = 19;
const COLS = 5;
const COLLAPSE_INTERVAL = 9;
const FIRST_COLLAPSE = 8;

/** SC-10 (1:14-1:24): 19 journal covers collapse one by one; final collapse shakes the camera; cuts to 0.3s black. */
export const SC10: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const durationInFrames = 10 * fps;
  const blackHoldFrames = Math.round(0.3 * fps);

  if (frame >= durationInFrames - blackHoldFrames) {
    return <SceneShell background="#000000" />;
  }

  const lastCollapseFrame = FIRST_COLLAPSE + (JOURNAL_COUNT - 1) * COLLAPSE_INTERVAL;
  const shakeActive = frame >= lastCollapseFrame && frame < lastCollapseFrame + 10;
  const rand = seededRandom(frame);
  const shakeX = shakeActive ? (rand() - 0.5) * width * 0.01 : 0;
  const shakeY = shakeActive ? (rand() - 0.5) * height * 0.01 : 0;

  const cellW = width * 0.13;
  const cellH = cellW * 1.3;
  const rows = Math.ceil(JOURNAL_COUNT / COLS);
  const gridW = cellW * COLS + 20 * (COLS - 1);
  const gridH = cellH * rows + 20 * (rows - 1);
  const left = width / 2 - gridW / 2;
  const top = height / 2 - gridH / 2;

  return (
    <SceneShell>
      <AbsoluteFill style={{ transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        {Array.from({ length: JOURNAL_COUNT }).map((_, i) => {
          const collapseFrame = FIRST_COLLAPSE + i * COLLAPSE_INTERVAL;
          const scaleY = interpolate(frame, [collapseFrame, collapseFrame + 5], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const row = Math.floor(i / COLS);
          const col = i % COLS;
          const seedRand = seededRandom(i * 17 + 3);
          const hue = 180 + seedRand() * 140;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: left + col * (cellW + 20),
                top: top + row * (cellH + 20),
                width: cellW,
                height: cellH,
                background: `hsl(${hue}, 30%, 70%)`,
                transform: `scaleY(${scaleY})`,
                transformOrigin: "center",
                borderRadius: 3,
              }}
            />
          );
        })}
      </AbsoluteFill>
    </SceneShell>
  );
};
