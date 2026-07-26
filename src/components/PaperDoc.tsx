import React from 'react';
import {COLORS} from '../theme';

// A single stylized "paper" — a rectangle with a header bar and text-line
// rules, standing in for a research paper without needing real content.
export const PaperDoc: React.FC<{
  width: number;
  height: number;
  seed: number;
  accent?: string;
  flagged?: boolean;
}> = ({width, height, seed, accent = COLORS.textDim, flagged = false}) => {
  const lineCount = 6 + (seed % 4);
  const lines = new Array(lineCount).fill(0);

  return (
    <div
      style={{
        width,
        height,
        background: '#10152A',
        border: `2px solid ${flagged ? COLORS.red : '#232B49'}`,
        borderRadius: 6,
        padding: width * 0.08,
        boxSizing: 'border-box',
        boxShadow: flagged ? `0 0 24px ${COLORS.red}55` : 'none',
        display: 'flex',
        flexDirection: 'column',
        gap: height * 0.045,
      }}
    >
      <div
        style={{
          width: '60%',
          height: height * 0.05,
          background: flagged ? COLORS.red : accent,
          borderRadius: 2,
          opacity: 0.9,
        }}
      />
      {lines.map((_, i) => (
        <div
          key={i}
          style={{
            width: `${70 + ((seed + i * 13) % 30)}%`,
            height: height * 0.028,
            background: COLORS.textDim,
            opacity: 0.35,
            borderRadius: 2,
          }}
        />
      ))}
    </div>
  );
};
