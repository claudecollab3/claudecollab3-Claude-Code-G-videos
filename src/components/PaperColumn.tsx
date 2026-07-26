import React from "react";
import { COLORS } from "../constants/theme";
import { jitterFor } from "../utils/seededRandom";

type Props = {
  /** How many sheets are visible in the current viewport window. */
  count: number;
  /** Vertical scroll offset in px — increase to make the column climb/scroll. */
  scrollY: number;
  width: number;
  height: number;
  sheetWidth?: number;
  sheetHeight?: number;
  spacing?: number;
  /** Renders sheets desaturated gray instead of bone-white. */
  monochrome?: boolean;
  /** Index (from the bottom, 0-based) of a single sheet to flare flagged-red. */
  flareIndex?: number;
  /** Fraction [0,1] of the horizontal spread — 0 keeps sheets in a tight column. */
  spread?: number;
};

/**
 * A tall column of paper-sheet rectangles, used by SC-01/02/11/23/24. Sheets
 * are positioned by a seeded jitter so the column reads as an organic stack
 * rather than a rigid grid, and is fully frame-driven via `scrollY`.
 */
export const PaperColumn: React.FC<Props> = ({
  count,
  scrollY,
  width,
  height,
  sheetWidth = 90,
  sheetHeight = 120,
  spacing = 34,
  monochrome = false,
  flareIndex,
  spread = 0.07,
}) => {
  const centerX = width / 2;
  const sheets = [];
  for (let i = 0; i < count; i++) {
    const y = height - i * spacing - scrollY;
    if (y < -sheetHeight - 40 || y > height + 40) continue;
    const j = jitterFor(i);
    const x = centerX + (j.x - 0.5) * width * spread - sheetWidth / 2;
    const rotation = (j.r - 0.5) * 6;
    const isFlared = flareIndex === i;
    sheets.push(
      <div
        key={i}
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: sheetWidth,
          height: sheetHeight,
          background: isFlared ? COLORS.flagged : monochrome ? "#9AA0AC" : COLORS.text,
          borderRadius: 4,
          transform: `rotate(${rotation}deg)`,
          boxShadow: isFlared
            ? `0 0 40px 8px ${COLORS.flagged}`
            : "0 4px 14px rgba(0,0,0,0.35)",
          opacity: monochrome && !isFlared ? 0.55 : 1,
        }}
      >
        <div
          style={{
            margin: "14px 12px 0 12px",
            height: 3,
            background: "rgba(10,14,26,0.25)",
          }}
        />
        <div
          style={{
            margin: "10px 12px 0 12px",
            height: 3,
            width: "70%",
            background: "rgba(10,14,26,0.2)",
          }}
        />
      </div>,
    );
  }
  return <>{sheets}</>;
};
