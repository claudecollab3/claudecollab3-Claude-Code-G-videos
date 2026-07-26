import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

// A restrained lower-third caption of the current VO line. Fades in/out;
// does not attempt word-level karaoke sync.
export const Caption: React.FC<{
  text: string;
  color?: string;
}> = ({text, color = COLORS.text}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <>
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 420,
          background: 'linear-gradient(to top, rgba(5,7,16,0.95) 30%, transparent)',
          opacity,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: 90,
          left: 140,
          right: 140,
          opacity,
        }}
      >
        <p
          style={{
            fontFamily: bodyFontFamily,
            fontWeight: 500,
            fontSize: 40,
            lineHeight: 1.35,
            color,
            margin: 0,
          }}
        >
          {text}
        </p>
      </div>
    </>
  );
};
