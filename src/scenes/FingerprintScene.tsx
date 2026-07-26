import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const RING_COUNT = 22;
const CX = 960;
const CY = 540;

const mulberry32 = (seed: number) => {
  let a = seed;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

export const FingerprintScene: React.FC = () => {
  const frame = useCurrentFrame();

  const rings = useMemo(() => {
    const rand = mulberry32(7);
    return new Array(RING_COUNT).fill(0).map((_, i) => {
      const rx = 90 + i * 26 + rand() * 10;
      const ry = rx * (0.55 + rand() * 0.1);
      const rotation = -18 + rand() * 10;
      const gapStart = rand() * 360;
      const gapSize = 20 + rand() * 50;
      const highlighted = rand() < 0.22;
      return {rx, ry, rotation, gapStart, gapSize, highlighted, seed: i};
    });
  }, []);

  return (
    <Background>
      <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
        {rings.map((ring, i) => {
          const drawStart = 10 + i * 6;
          const draw = interpolate(frame, [drawStart, drawStart + 24], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const circumference = Math.PI * (ring.rx + ring.ry);
          const visibleLen = circumference * ((360 - ring.gapSize) / 360) * draw;
          return (
            <ellipse
              key={i}
              cx={CX}
              cy={CY}
              rx={ring.rx}
              ry={ring.ry}
              transform={`rotate(${ring.rotation} ${CX} ${CY})`}
              fill="none"
              stroke={ring.highlighted ? COLORS.red : COLORS.teal}
              strokeWidth={ring.highlighted ? 5 : 2.5}
              strokeOpacity={ring.highlighted ? 0.9 : 0.35}
              strokeDasharray={`${visibleLen} ${circumference}`}
              strokeDashoffset={-(ring.gapStart / 360) * circumference}
              strokeLinecap="round"
              style={ring.highlighted ? {filter: `drop-shadow(0 0 8px ${COLORS.red})`} : undefined}
            />
          );
        })}
      </svg>

      <div style={{position: 'absolute', top: 90, left: 140, display: 'flex', flexDirection: 'column', gap: 6}}>
        <div
          style={{
            fontFamily: bodyFontFamily,
            fontSize: 26,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: COLORS.textDim,
          }}
        >
          The Template Fingerprint
        </div>
      </div>
    </Background>
  );
};
