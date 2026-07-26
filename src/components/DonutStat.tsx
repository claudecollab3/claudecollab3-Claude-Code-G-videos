import React from "react";
import { PieChart, Pie, Cell } from "recharts";
import { COLORS, FONTS } from "../constants/theme";

type Props = {
  /** 0-100 target percentage. */
  percent: number;
  progress: number; // 0-1, frame-driven fill progress (recharts' own animation is real-time, not frame-safe)
  color: string;
  label: string;
  size?: number;
  fontScale?: number;
};

/** Frame-driven donut (recharts animation is wall-clock, so fill is computed externally per frame). */
export const DonutStat: React.FC<Props> = ({ percent, progress, color, label, size = 260, fontScale = 1 }) => {
  const filled = percent * progress;
  const data = [
    { name: "filled", value: filled },
    { name: "rest", value: 100 - filled },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <div style={{ position: "relative", width: size, height: size }}>
        <PieChart width={size} height={size}>
          <Pie
            data={data}
            dataKey="value"
            cx="50%"
            cy="50%"
            innerRadius={size * 0.34}
            outerRadius={size * 0.46}
            startAngle={90}
            endAngle={450}
            isAnimationActive={false}
            stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="#1B2233" />
          </Pie>
        </PieChart>
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span
            style={{
              fontFamily: FONTS.numeral,
              fontWeight: 700,
              fontSize: 54 * fontScale,
              color: COLORS.text,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {filled.toFixed(percent % 1 !== 0 ? 2 : 0)}%
          </span>
        </div>
      </div>
      <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 24 * fontScale, color, letterSpacing: "0.04em" }}>
        {label}
      </div>
    </div>
  );
};
