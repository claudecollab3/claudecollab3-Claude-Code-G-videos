import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { COLORS, FONTS } from "../constants/theme";
import { FLAGGED_SHARE_BY_YEAR } from "../data/flaggedShareByYear";

type Props = {
  width: number;
  height: number;
  /** 0-1 left-to-right reveal progress, driven by the caller's frame. */
  progress: number;
  showTopDecile?: boolean;
  fontScale?: number;
};

/** Flagged-share-by-year line chart with a frame-driven left-to-right reveal (clip-based, since recharts' own animation is wall-clock). */
export const LineChartReveal: React.FC<Props> = ({ width, height, progress, showTopDecile = false, fontScale = 1 }) => {
  return (
    <div style={{ position: "relative", width, height }}>
      <LineChart width={width} height={height} data={FLAGGED_SHARE_BY_YEAR} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
        <CartesianGrid stroke="#232B40" vertical={false} />
        <XAxis
          dataKey="year"
          stroke="#5B6478"
          tick={{ fill: COLORS.text, fontFamily: FONTS.body, fontSize: 16 * fontScale }}
        />
        <YAxis
          stroke="#5B6478"
          tick={{ fill: COLORS.text, fontFamily: FONTS.body, fontSize: 16 * fontScale }}
          unit="%"
        />
        <Line type="monotone" dataKey="all" stroke={COLORS.flagged} strokeWidth={4} dot={false} isAnimationActive={false} />
        {showTopDecile && (
          <Line type="monotone" dataKey="topDecile" stroke={COLORS.uncertain} strokeWidth={3} strokeDasharray="6 5" dot={false} isAnimationActive={false} />
        )}
      </LineChart>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: `${progress * 100}%`,
          right: 0,
          bottom: 0,
          background: COLORS.bg,
        }}
      />
    </div>
  );
};
