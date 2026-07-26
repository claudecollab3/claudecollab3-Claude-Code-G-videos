import React from 'react';
import {Audio, interpolate, staticFile} from 'remotion';
import {TIMELINE} from '../Schedule';

const DUCKED = 0.14;
const BED = 0.32;
const TITLE_PEAK = 0.32;
const RAMP = 16;

const volumeAtFrame = (frame: number): number => {
  const block = TIMELINE.find((b) => frame >= b.startFrame && frame < b.endFrame);
  if (!block) return 0;

  if (block.kind === 'title') {
    return interpolate(frame, [block.startFrame, block.startFrame + 30], [0, TITLE_PEAK], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  if (block.kind === 'interstitial') {
    if (block.silent) {
      // The full audio drop right before the twist.
      const fadeOut = interpolate(frame, [block.startFrame - RAMP, block.startFrame], [1, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
      return fadeOut * BED;
    }
    const fadeIn = interpolate(frame, [block.startFrame, block.startFrame + RAMP], [0, BED], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    return Math.min(fadeIn, BED);
  }

  // Segment block: duck under the narration, breathe back up during the hold.
  const {startFrame, voEndFrame} = block;
  if (frame < voEndFrame) {
    return interpolate(frame, [startFrame, startFrame + RAMP], [BED, DUCKED], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }
  return interpolate(frame, [voEndFrame, voEndFrame + RAMP], [DUCKED, BED], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};

const TOTAL = TIMELINE[TIMELINE.length - 1].endFrame;

export const AmbientDrone: React.FC = () => {
  return (
    <Audio
      src={staticFile('audio/ambient_drone.mp3')}
      volume={(f) => {
        const fadeTail = interpolate(f, [TOTAL - 60, TOTAL - 5], [1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return volumeAtFrame(f) * fadeTail;
      }}
    />
  );
};
