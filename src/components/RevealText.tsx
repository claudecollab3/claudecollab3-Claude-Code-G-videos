import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

// Word-by-word reveal, paced across `durationInFrames` so the last word
// lands slightly before the VO line ends. Optional keyword list recolors
// matching words (case-insensitive, punctuation-stripped match).
export const RevealText: React.FC<{
  text: string;
  durationInFrames: number;
  fontSize?: number;
  maxWidth?: number;
  keywords?: {words: string[]; color: string}[];
}> = ({text, durationInFrames, fontSize = 56, maxWidth = 1400, keywords = []}) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const revealSpan = durationInFrames * 0.82;

  const colorFor = (word: string) => {
    const clean = word.toLowerCase().replace(/[.,;:—()]/g, '');
    for (const group of keywords) {
      if (group.words.some((w) => clean.includes(w))) return group.color;
    }
    return COLORS.text;
  };

  return (
    <div
      style={{
        maxWidth,
        fontFamily: bodyFontFamily,
        fontWeight: 600,
        fontSize,
        lineHeight: 1.4,
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.28em',
      }}
    >
      {words.map((word, i) => {
        const start = (i / words.length) * revealSpan;
        const opacity = interpolate(frame, [start, start + 10], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const y = interpolate(frame, [start, start + 10], [14, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return (
          <span
            key={i}
            style={{
              opacity,
              transform: `translateY(${y}px)`,
              color: colorFor(word),
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
