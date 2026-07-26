import React from 'react';
import {interpolate, useCurrentFrame, Easing} from 'remotion';
import {condensedFontFamily} from '../fonts';

export const CountUp: React.FC<{
  from?: number;
  to: number;
  startFrame?: number;
  durationInFrames?: number;
  format?: (n: number) => string;
  color: string;
  fontSize?: number;
  suffix?: string;
}> = ({
  from = 0,
  to,
  startFrame = 0,
  durationInFrames = 45,
  format,
  color,
  fontSize = 140,
  suffix = '',
}) => {
  const frame = useCurrentFrame();
  const value = interpolate(
    frame,
    [startFrame, startFrame + durationInFrames],
    [from, to],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    },
  );
  const display = format ? format(value) : Math.round(value).toLocaleString('en-US');

  return (
    <span
      style={{
        fontFamily: condensedFontFamily,
        fontWeight: 600,
        fontSize,
        color,
        fontVariantNumeric: 'tabular-nums',
        letterSpacing: '0.01em',
      }}
    >
      {display}
      {suffix}
    </span>
  );
};
