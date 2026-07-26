import React from "react";
import { AbsoluteFill } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const GRID_SIZE = 6;
const FLAGGED_CELLS = [2, 9, 14, 21, 27, 33];

/**
 * Static (non-animating) frame used as both the very first and very last
 * Sequence of ShortsCut, per the hard-loop requirement: since neither
 * instance depends on its local frame number, frame 0 of the opening
 * instance and the final frame of the closing instance render pixel-
 * identical, making the loop seamless.
 */
export const LoopBookend: React.FC<SceneProps> = ({ aspect }) => {
  const { width, fontScale } = useSceneLayout(aspect);
  const cellSize = width * 0.5 / GRID_SIZE;
  const gridLeft = width / 2 - (cellSize * GRID_SIZE) / 2;

  const cells = [];
  for (let i = 0; i < GRID_SIZE * GRID_SIZE; i++) {
    const row = Math.floor(i / GRID_SIZE);
    const col = i % GRID_SIZE;
    const isFlagged = FLAGGED_CELLS.includes(i);
    cells.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: gridLeft + col * cellSize,
          top: 120 + row * cellSize,
          width: cellSize - 6,
          height: cellSize - 6,
          background: isFlagged ? COLORS.flagged : "#2A3040",
          borderRadius: 3,
        }}
      />,
    );
  }

  return (
    <SceneShell>
      <AbsoluteFill>{cells}</AbsoluteFill>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 140 }}>
        <AnimatedCounter to={142_857} from={142_857} fontSize={80 * fontScale} color={COLORS.flagged} />
        <div
          style={{
            marginTop: 10,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 24 * fontScale,
            color: COLORS.text,
            letterSpacing: "0.04em",
          }}
        >
          FLAGGED, NOT PROVEN
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
