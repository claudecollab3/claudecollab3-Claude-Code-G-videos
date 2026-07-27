import {useCurrentFrame} from 'remotion';
import {mulberry32, hashSeed} from './random';

export type StopMotionJitter = {
  x: number;
  y: number;
  rotation: number;
  heldFrame: number;
  transform: string;
};

export type StopMotionJitterOptions = {
  /** Hold every Nth frame — 3 = 10fps holds, 2 = 15fps holds, on a 30fps timeline. */
  holdFrames?: number;
  /** Max position jitter in px (applied as +/- posAmp). */
  posAmp?: number;
  /** Max rotation jitter in degrees (applied as +/- rotAmp). */
  rotAmp?: number;
};

/**
 * Simulates a puppet nudged slightly between stop-motion shots: position
 * updates only every `holdFrames` frames (instead of every frame), and each
 * held frame gets a tiny deterministic random jitter derived from `seed`.
 * Two elements with different seeds will jitter differently even on the
 * same held frame, so a whole scene doesn't "breathe" in unison.
 */
export const useStopMotionJitter = (
  seed: number,
  options: StopMotionJitterOptions = {},
): StopMotionJitter => {
  const frame = useCurrentFrame();
  const holdFrames = options.holdFrames ?? 3;
  const posAmp = options.posAmp ?? 1.6;
  const rotAmp = options.rotAmp ?? 0.3;

  const heldFrame = Math.floor(frame / holdFrames) * holdFrames;
  const rand = mulberry32(hashSeed(seed, heldFrame));

  const x = (rand() - 0.5) * 2 * posAmp;
  const y = (rand() - 0.5) * 2 * posAmp;
  const rotation = (rand() - 0.5) * 2 * rotAmp;

  return {
    x,
    y,
    rotation,
    heldFrame,
    transform: `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) rotate(${rotation.toFixed(2)}deg)`,
  };
};
