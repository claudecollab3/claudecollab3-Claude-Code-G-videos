import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {condensedFontFamily, bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const DOT_COUNT = 240;

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

export const SplitStatScene: React.FC = () => {
  const frame = useCurrentFrame();
  const rand = mulberry32(99);
  const dots = new Array(DOT_COUNT).fill(0).map((_, i) => ({
    x: rand() * 640,
    y: rand() * 640,
    delay: (i % 60) * 3,
  }));

  const paperOpacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <Background>
      <div style={{position: 'absolute', inset: 0, display: 'flex'}}>
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            borderRight: `1px solid ${COLORS.grid}`,
            gap: 24,
          }}
        >
          <svg width={640} height={640} viewBox="0 0 640 640">
            {dots.map((d, i) => {
              const o = interpolate(frame, [d.delay, d.delay + 12], [0, 0.85], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              });
              return <circle key={i} cx={d.x} cy={d.y} r={3.2} fill={COLORS.teal} opacity={o} />;
            })}
          </svg>
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
            <div style={{fontFamily: condensedFontFamily, fontWeight: 600, fontSize: 56, color: COLORS.teal}}>
              Detect: Millions
            </div>
            <div style={{fontFamily: bodyFontFamily, fontSize: 24, color: COLORS.textDim}}>
              at once, by machine
            </div>
          </div>
        </div>

        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 24,
          }}
        >
          <div
            style={{
              width: 220,
              height: 290,
              background: '#10152A',
              border: `3px solid ${COLORS.amber}`,
              borderRadius: 10,
              opacity: paperOpacity,
              boxShadow: `0 0 40px ${COLORS.amber}55`,
              padding: 26,
              display: 'flex',
              flexDirection: 'column',
              gap: 14,
            }}
          >
            <div style={{width: '60%', height: 14, background: COLORS.amber, borderRadius: 2}} />
            {new Array(6).fill(0).map((_, i) => (
              <div key={i} style={{width: `${70 + (i % 3) * 10}%`, height: 8, background: COLORS.textDim, opacity: 0.4, borderRadius: 2}} />
            ))}
          </div>
          <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
            <div style={{fontFamily: condensedFontFamily, fontWeight: 600, fontSize: 56, color: COLORS.amber}}>
              Verify: One At A Time
            </div>
            <div style={{fontFamily: bodyFontFamily, fontSize: 24, color: COLORS.textDim}}>
              by a human expert
            </div>
          </div>
        </div>
      </div>
    </Background>
  );
};
