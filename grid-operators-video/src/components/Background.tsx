import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS} from '../theme';
import {GrainOverlay} from './GrainOverlay';
import {HandheldCamera} from './HandheldCamera';

/**
 * The "tabletop": warm off-white background with a soft vignette, global
 * paper grain, and a subtle handheld camera drift wrapping the scene
 * content. Every scene should render its cutouts inside this.
 */
export const Background: React.FC<{
  seed?: string | number;
  children?: React.ReactNode;
}> = ({seed = 'scene', children}) => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 70% 60% at 50% 40%, ${COLORS.bg} 0%, ${COLORS.bg} 45%, ${COLORS.bgVignette} 100%)`,
        }}
      />
      <HandheldCamera seed={seed}>{children}</HandheldCamera>
      <GrainOverlay />
    </AbsoluteFill>
  );
};
