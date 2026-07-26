import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {PaperDoc} from '../components/PaperDoc';
import {COLORS} from '../theme';

// Infinite scrolling columns of documents, drifting upward, suggesting an
// unmanageable volume of papers. A handful are pre-seeded "flagged" red.
const NUM_COLUMNS = 9;
const CARD_W = 190;
const CARD_H = 250;
const GAP = 34;
const CELL = CARD_H + GAP;

const Column: React.FC<{
  index: number;
  speed: number;
  frame: number;
}> = ({index, speed, frame}) => {
  const offset = (frame * speed) % CELL;
  const cardsNeeded = Math.ceil(1080 / CELL) + 2;

  return (
    <div
      style={{
        position: 'absolute',
        left: index * (CARD_W + GAP) + 60,
        top: -CELL + offset,
        display: 'flex',
        flexDirection: 'column',
        gap: GAP,
      }}
    >
      {new Array(cardsNeeded).fill(0).map((_, i) => {
        const seed = index * 97 + i * 31;
        const flagged = seed % 11 === 0;
        return (
          <PaperDoc
            key={i}
            width={CARD_W}
            height={CARD_H}
            seed={seed}
            flagged={flagged}
          />
        );
      })}
    </div>
  );
};

export const PaperColumnScene: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <Background>
      <AbsoluteFill style={{overflow: 'hidden'}}>
        {new Array(NUM_COLUMNS).fill(0).map((_, i) => (
          <Column
            key={i}
            index={i}
            speed={i % 2 === 0 ? 1.4 : 1.9}
            frame={frame}
          />
        ))}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `linear-gradient(to bottom, ${COLORS.bg} 0%, transparent 18%, transparent 82%, ${COLORS.bg} 100%)`,
        }}
      />
    </Background>
  );
};
