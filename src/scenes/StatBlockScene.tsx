import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {CountUp} from '../components/CountUp';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const STATS: {label: string; to: number; suffix?: string; startFrame: number}[] = [
  {label: 'Suspected papers, 20 years', to: 400000, suffix: '+', startFrame: 15},
  {label: 'One publisher retracted', to: 11000, startFrame: 55},
  {label: 'Journals shut down', to: 19, startFrame: 95},
];

export const StatBlockScene: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <Background>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 110,
          padding: '0 140px',
        }}
      >
        {STATS.map((stat, i) => {
          const appear = interpolate(frame, [stat.startFrame - 10, stat.startFrame], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <div
              key={i}
              style={{
                opacity: appear,
                transform: `translateY(${(1 - appear) * 20}px)`,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 16,
                textAlign: 'center',
              }}
            >
              <CountUp
                to={stat.to}
                startFrame={stat.startFrame}
                durationInFrames={55}
                color={COLORS.red}
                fontSize={110}
                suffix={stat.suffix}
              />
              <div
                style={{
                  fontFamily: bodyFontFamily,
                  fontSize: 26,
                  color: COLORS.textDim,
                  maxWidth: 260,
                }}
              >
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>
    </Background>
  );
};
