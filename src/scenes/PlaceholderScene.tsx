import React from 'react';
import {Background} from '../components/Background';
import {Caption} from '../components/Caption';
import {condensedFontFamily} from '../fonts';
import {COLORS} from '../theme';

// Temporary stand-in scene used for segments that don't have a bespoke
// visual yet. Keeps the timeline renderable end-to-end during build-out.
export const PlaceholderScene: React.FC<{label: string; text: string}> = ({
  label,
  text,
}) => {
  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: 140,
          fontFamily: condensedFontFamily,
          fontSize: 26,
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: COLORS.amber,
          opacity: 0.7,
        }}
      >
        {label}
      </div>
      <Caption text={text} />
    </Background>
  );
};
