import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { COLORS, FONTS } from "../constants/theme";

const formatNumber = (n: number, decimals: number) => {
  const fixed = n.toFixed(decimals);
  const [intPart, decPart] = fixed.split(".");
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return decPart ? `${withCommas}.${decPart}` : withCommas;
};

type Props = {
  /** Value the counter lands on. */
  to: number;
  /** Value the counter starts from. Default 0. */
  from?: number;
  /** Frame (relative to this component's Sequence) the count-up starts. */
  startFrame?: number;
  /** How many decimal places to show. */
  decimals?: number;
  /** Prefix/suffix, e.g. "$" or "%". */
  prefix?: string;
  suffix?: string;
  fontSize?: number;
  color?: string;
  /** Duration of the ease-out count in ms — spec default is 280ms. */
  durationMs?: number;
  bold?: boolean;
};

export const AnimatedCounter: React.FC<Props> = ({
  to,
  from = 0,
  startFrame = 0,
  decimals = 0,
  prefix = "",
  suffix = "",
  fontSize = 120,
  color = COLORS.text,
  durationMs = 280,
  bold = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationInFrames = (durationMs / 1000) * fps;

  const value = interpolate(frame, [startFrame, startFrame + durationInFrames], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <span
      style={{
        fontFamily: FONTS.numeral,
        fontWeight: bold ? 700 : 500,
        fontSize,
        color,
        fontVariantNumeric: "tabular-nums",
        letterSpacing: "0.01em",
      }}
    >
      {prefix}
      {formatNumber(value, decimals)}
      {suffix}
    </span>
  );
};
