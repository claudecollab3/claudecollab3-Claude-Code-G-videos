import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Background} from '../components/Background';
import {condensedFontFamily} from '../fonts';
import {COLORS} from '../theme';

export const Interstitial: React.FC<{label: string; silent?: boolean}> = ({
  label,
  silent,
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opacity = interpolate(
    frame,
    [0, 10, durationInFrames - 12, durationInFrames],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const trackIn = interpolate(frame, [0, 20], [24, 0], {
    extrapolateRight: 'clamp',
  });

  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            opacity,
            transform: `translateY(${trackIn}px)`,
            display: 'flex',
            alignItems: 'center',
            gap: 28,
          }}
        >
          <div
            style={{
              width: 64,
              height: 4,
              background: silent ? COLORS.red : COLORS.textDim,
            }}
          />
          <div
            style={{
              fontFamily: condensedFontFamily,
              fontWeight: 600,
              fontSize: 64,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              color: silent ? COLORS.red : COLORS.text,
            }}
          >
            {label}
          </div>
          <div
            style={{
              width: 64,
              height: 4,
              background: silent ? COLORS.red : COLORS.textDim,
            }}
          />
        </div>
      </div>
    </Background>
  );
};
