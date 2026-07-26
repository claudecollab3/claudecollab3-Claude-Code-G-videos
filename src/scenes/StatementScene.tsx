import React from 'react';
import {Background} from '../components/Background';
import {RevealText} from '../components/RevealText';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

export const StatementScene: React.FC<{
  eyebrow: string;
  text: string;
  durationInFrames: number;
  keywords?: {words: string[]; color: string}[];
}> = ({eyebrow, text, durationInFrames, keywords}) => {
  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'flex-start',
          padding: '0 220px',
          gap: 28,
        }}
      >
        <div
          style={{
            fontFamily: bodyFontFamily,
            fontSize: 26,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: COLORS.textDim,
          }}
        >
          {eyebrow}
        </div>
        <RevealText text={text} durationInFrames={durationInFrames} keywords={keywords} />
      </div>
    </Background>
  );
};
