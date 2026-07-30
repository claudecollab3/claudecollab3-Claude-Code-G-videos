import React from "react";

interface EquityPoint {
  timestamp: string;
  equity: number;
}

const WIDTH = 640;
const HEIGHT = 220;
const PADDING = 12;

export default function EquityCurveChart({ points }: { points: EquityPoint[] }) {
  if (points.length < 2) {
    return <p className="hint">Not enough data to draw an equity curve yet.</p>;
  }

  const equities = points.map((p) => p.equity);
  const min = Math.min(...equities);
  const max = Math.max(...equities);
  const range = max - min || 1;

  const coords = points.map((p, i) => {
    const x = PADDING + (i / (points.length - 1)) * (WIDTH - PADDING * 2);
    const y = HEIGHT - PADDING - ((p.equity - min) / range) * (HEIGHT - PADDING * 2);
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });

  const isProfit = points[points.length - 1].equity >= points[0].equity;
  const strokeColor = isProfit ? "#22c55e" : "#ef4444";

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="equity-chart" role="img" aria-label="Equity curve">
      <polyline points={coords.join(" ")} fill="none" stroke={strokeColor} strokeWidth={2} />
    </svg>
  );
}
