import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {CountUp} from '../components/CountUp';
import {condensedFontFamily, bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const GRID = 10;
const CELL = 46;
const GAP = 10;
// The 10 cells (of 100) that flip red — a diagonal-ish scatter so it doesn't
// read as a literal fraction bar.
const FLAGGED_INDICES = new Set([4, 17, 23, 38, 44, 55, 61, 72, 86, 93]);

export const GridFlipScene: React.FC = () => {
  const frame = useCurrentFrame();
  const gridSize = GRID * CELL + (GRID - 1) * GAP;

  const flaggedOrder = Array.from(FLAGGED_INDICES);

  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 140,
        }}
      >
        <div
          style={{
            width: gridSize,
            height: gridSize,
            display: 'grid',
            gridTemplateColumns: `repeat(${GRID}, ${CELL}px)`,
            gridTemplateRows: `repeat(${GRID}, ${CELL}px)`,
            gap: GAP,
          }}
        >
          {new Array(GRID * GRID).fill(0).map((_, i) => {
            const flagIndex = flaggedOrder.indexOf(i);
            const flipStart = 20 + (flagIndex >= 0 ? flagIndex * 14 : 0);
            const flip = flagIndex >= 0
              ? interpolate(frame, [flipStart, flipStart + 12], [0, 1], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                })
              : 0;
            const rotateY = flip * 180;
            const isBack = flip > 0.5;
            return (
              <div
                key={i}
                style={{
                  width: CELL,
                  height: CELL,
                  borderRadius: 4,
                  background: isBack ? COLORS.red : '#161C34',
                  border: `1px solid ${isBack ? COLORS.red : '#262E4E'}`,
                  transform: `perspective(300px) rotateY(${rotateY}deg)`,
                  boxShadow: isBack ? `0 0 18px ${COLORS.red}77` : 'none',
                }}
              />
            );
          })}
        </div>

        <div style={{display: 'flex', flexDirection: 'column', gap: 10}}>
          <div
            style={{
              fontFamily: bodyFontFamily,
              fontSize: 26,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: COLORS.textDim,
            }}
          >
            Flagged Share
          </div>
          <CountUp
            to={250000}
            startFrame={30}
            durationInFrames={110}
            color={COLORS.red}
            fontSize={128}
            format={(n) => Math.round(n).toLocaleString('en-US')}
          />
          <div
            style={{
              fontFamily: condensedFontFamily,
              fontWeight: 600,
              fontSize: 40,
              color: COLORS.text,
            }}
          >
            roughly <span style={{color: COLORS.red}}>1 in 10</span>
          </div>
        </div>
      </div>
    </Background>
  );
};
