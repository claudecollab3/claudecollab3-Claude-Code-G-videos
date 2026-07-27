import React from 'react';
import {useCurrentFrame} from 'remotion';
import {noise2D} from '@remotion/noise';

export type HandheldCameraProps = {
  seed?: string | number;
  /** How fast the drift wanders — lower is slower/dreamier. */
  speed?: number;
  /** Max pan in px. */
  panAmp?: number;
  /** Max tilt in degrees. */
  tiltAmp?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
};

/**
 * Wraps a scene in a very slow, Perlin-noise-driven pan/tilt so static shots
 * feel like they're resting on a tripod nudged by a hand, not locked off —
 * subtle enough to be felt rather than seen.
 */
export const HandheldCamera: React.FC<HandheldCameraProps> = ({
  seed = 'camera',
  speed = 0.006,
  panAmp = 5,
  tiltAmp = 0.35,
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const t = frame * speed;

  const x = noise2D(`${seed}-x`, t, 0) * panAmp;
  const y = noise2D(`${seed}-y`, t, 0) * panAmp * 0.6;
  const rotate = noise2D(`${seed}-r`, t, 0) * tiltAmp;
  const scale = 1.03; // slight overscan so the drift never reveals an edge

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        ...style,
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          transform: `scale(${scale}) translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) rotate(${rotate.toFixed(3)}deg)`,
        }}
      >
        {children}
      </div>
    </div>
  );
};
