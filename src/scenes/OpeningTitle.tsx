import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {condensedFontFamily, bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

export const OpeningTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15, 60, 75], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = interpolate(frame, [0, 20], [1.04, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          opacity,
          transform: `scale(${scale})`,
          textAlign: 'center',
          padding: '0 220px',
        }}
      >
        <div
          style={{
            fontFamily: bodyFontFamily,
            fontWeight: 600,
            fontSize: 28,
            letterSpacing: '0.35em',
            color: COLORS.red,
            textTransform: 'uppercase',
            marginBottom: 28,
          }}
        >
          2.6 Million Papers
        </div>
        <div
          style={{
            fontFamily: condensedFontFamily,
            fontWeight: 600,
            fontSize: 86,
            lineHeight: 1.15,
            color: COLORS.text,
          }}
        >
          An AI Read 2.6 Million Cancer Papers.
          <br />
          <span style={{color: COLORS.red}}>250,000 Came Back Flagged.</span>
        </div>
      </div>
    </Background>
  );
};
