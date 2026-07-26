import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const GRID_SIZE = 10;
// 10 non-adjacent, scattered cells (one per row, spread across columns).
const FLAGGED_CELLS = [1, 16, 23, 38, 40, 55, 62, 79, 84, 97];
const TICK_INTERVAL_FRAMES = 14;
const FIRST_TICK_FRAME = 10;

export const SC03: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { width, height, fontScale, isVertical } = useSceneLayout(aspect);

  const cellSize = (isVertical ? width * 0.72 : height * 0.62) / GRID_SIZE;
  const gridWidth = cellSize * GRID_SIZE;
  const gridHeight = cellSize * GRID_SIZE;
  const gridLeft = width / 2 - gridWidth / 2;
  const gridTop = isVertical ? height * 0.16 : height / 2 - gridHeight / 2 - 40;

  const textRevealFrame = FIRST_TICK_FRAME + FLAGGED_CELLS.length * TICK_INTERVAL_FRAMES + 6;
  const textOpacity = interpolate(frame, [textRevealFrame, textRevealFrame + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cells = [];
  for (let i = 0; i < GRID_SIZE * GRID_SIZE; i++) {
    const row = Math.floor(i / GRID_SIZE);
    const col = i % GRID_SIZE;
    const flagOrder = FLAGGED_CELLS.indexOf(i);
    const isFlagged = flagOrder !== -1 && frame >= FIRST_TICK_FRAME + flagOrder * TICK_INTERVAL_FRAMES;
    const justFlipped =
      isFlagged && frame < FIRST_TICK_FRAME + flagOrder * TICK_INTERVAL_FRAMES + 6;
    const flipScale = justFlipped
      ? interpolate(
          frame,
          [
            FIRST_TICK_FRAME + flagOrder * TICK_INTERVAL_FRAMES,
            FIRST_TICK_FRAME + flagOrder * TICK_INTERVAL_FRAMES + 6,
          ],
          [0.6, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        )
      : 1;
    cells.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: gridLeft + col * cellSize,
          top: gridTop + row * cellSize,
          width: cellSize - 6,
          height: cellSize - 6,
          background: isFlagged ? COLORS.flagged : "#2A3040",
          borderRadius: 3,
          transform: `scale(${flipScale})`,
        }}
      />,
    );
  }

  return (
    <SceneShell>
      <AbsoluteFill>{cells}</AbsoluteFill>
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "flex-end",
          paddingBottom: isVertical ? height * 0.22 : height * 0.12,
          opacity: textOpacity,
        }}
      >
        <AnimatedCounter
          to={250_000}
          startFrame={textRevealFrame}
          fontSize={90 * fontScale}
          color={COLORS.flagged}
        />
        <div
          style={{
            marginTop: 10,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 28 * fontScale,
            color: COLORS.text,
            letterSpacing: "0.04em",
          }}
        >
          ≈ 1 IN 10 · FLAGGED, NOT PROVEN
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
