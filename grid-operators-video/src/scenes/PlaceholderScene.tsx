import React from 'react';
import {Background} from '../components/Background';
import {captionFontFamily} from '../fonts';
import {COLORS} from '../theme';

/** Stand-in for scenes not built yet, so the timeline renders end-to-end. */
export const PlaceholderScene: React.FC<{label: string}> = ({label}) => {
  return (
    <Background seed={label}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 80px',
          textAlign: 'center',
        }}
      >
        <div style={{fontFamily: captionFontFamily, fontSize: 34, color: COLORS.ink, opacity: 0.5}}>
          {label}
        </div>
      </div>
    </Background>
  );
};
