import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {CountUp} from '../components/CountUp';
import {generateDots} from '../components/worldRegions';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

export const WorldMapScene: React.FC<{
  variant: 'scope' | 'country';
}> = ({variant}) => {
  const frame = useCurrentFrame();
  const dots = useMemo(() => generateDots(46), []);

  // 'scope': flagged dots scattered evenly across every region (not one country).
  // 'country': flagged dots concentrated almost entirely in one region (Asia).
  const isFlagged = (d: (typeof dots)[number]) => {
    if (variant === 'scope') {
      return d.seed % 5 === 0;
    }
    if (d.region === 'as') return d.seed % 4 !== 0;
    return d.seed % 29 === 0;
  };

  return (
    <Background>
      <svg
        viewBox="0 0 1920 1080"
        width="100%"
        height="100%"
        style={{position: 'absolute', inset: 0}}
      >
        {dots.map((d, i) => {
          const flagged = isFlagged(d);
          const bloomStart = 15 + (i % 40) * 4;
          const bloom = interpolate(frame, [bloomStart, bloomStart + 18], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const baseOpacity = interpolate(frame, [0, 20], [0, 0.55], {
            extrapolateRight: 'clamp',
          });
          const color = flagged ? COLORS.red : COLORS.teal;
          const radius = flagged ? 3.5 + bloom * 4.5 : 3.5;
          const opacity = flagged ? baseOpacity + bloom * (1 - baseOpacity) : baseOpacity;
          return (
            <circle
              key={i}
              cx={d.x}
              cy={d.y}
              r={radius}
              fill={color}
              opacity={opacity}
              style={flagged ? {filter: `drop-shadow(0 0 6px ${COLORS.red})`} : undefined}
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
          {variant === 'scope' ? 'Every Region, Every Journal' : 'One Country’s Institutions'}
        </div>
        {variant === 'country' && (
          <CountUp
            to={170000}
            startFrame={20}
            durationInFrames={90}
            color={COLORS.red}
            fontSize={104}
            suffix="+"
          />
        )}
      </div>
    </Background>
  );
};
