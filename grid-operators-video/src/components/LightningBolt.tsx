import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {COLORS} from '../theme';
import {PaperShape} from './PaperShape';
import {useStopMotionJitter} from './useStopMotionJitter';
import {lightningBoltPath} from './shapes';

export const LightningBolt: React.FC<{
  seed: number;
  width?: number;
  height?: number;
  left: number;
  top: number;
  delayFrames?: number;
  color?: string;
}> = ({seed, width = 90, height = 260, left, top, delayFrames = 0, color = COLORS.charcoal}) => {
  const frame = useCurrentFrame() - delayFrames;
  const jitter = useStopMotionJitter(seed, {holdFrames: 3, posAmp: 2, rotAmp: 0.6});

  // Stop-motion "slam" entrance: held at -height, then snaps down in two
  // discrete steps rather than easing continuously.
  const slideProgress = interpolate(frame, [0, 9], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const stepped = Math.floor(slideProgress * 4) / 4;
  const yOffset = interpolate(stepped, [0, 1], [-height * 1.3, 0]);
  const opacity = interpolate(frame, [0, 4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const path = lightningBoltPath(width, height, seed);

  if (frame < 0) return null;

  return (
    <div
      style={{
        position: 'absolute',
        left,
        top,
        opacity,
        transform: `translateY(${yOffset}px) ${jitter.transform}`,
      }}
    >
      <PaperShape
        seed={seed}
        width={width}
        height={height}
        tornStrength={5}
        grainOpacity={0.14}
        shadow={{dx: 5, dy: 9, blur: 7, opacity: 0.3}}
      >
        <path d={path} fill={color} />
      </PaperShape>
    </div>
  );
};
