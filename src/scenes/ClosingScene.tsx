import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Background} from '../components/Background';
import {condensedFontFamily} from '../fonts';
import {COLORS} from '../theme';

export const ClosingScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const line1Opacity = interpolate(frame, [0, 15], [0, 1], {extrapolateRight: 'clamp'});
  const line2Opacity = interpolate(frame, [55, 75], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 45, durationInFrames - 5],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

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
          textAlign: 'center',
          padding: '0 200px',
          gap: 32,
          opacity: fadeOut,
        }}
      >
        <div
          style={{
            fontFamily: condensedFontFamily,
            fontWeight: 600,
            fontSize: 72,
            lineHeight: 1.25,
            color: COLORS.text,
            opacity: line1Opacity,
          }}
        >
          Who checks <span style={{color: COLORS.red}}>250,000 papers</span>?
        </div>
        <div
          style={{
            fontFamily: condensedFontFamily,
            fontWeight: 600,
            fontSize: 72,
            lineHeight: 1.25,
            color: COLORS.textDim,
            opacity: line2Opacity,
          }}
        >
          And what happens to the ones nobody gets to?
        </div>
      </div>
    </Background>
  );
};
