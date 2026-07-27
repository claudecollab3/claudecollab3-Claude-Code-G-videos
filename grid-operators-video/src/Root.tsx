import React from 'react';
import {Composition} from 'remotion';
import {MainVideo} from './MainVideo';
import {TOTAL_FRAMES} from './Schedule';
import {FPS, WIDTH, HEIGHT} from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Main"
        component={MainVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
