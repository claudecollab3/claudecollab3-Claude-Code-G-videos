import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {SCHEDULE, SceneId} from './Schedule';
import {Scene1Hook} from './scenes/Scene1Hook';
import {PlaceholderScene} from './scenes/PlaceholderScene';
import audioManifest from './audioManifest.json';
import {COLORS} from './theme';

const manifest = audioManifest as Record<string, string>;

const SceneFor: React.FC<{id: SceneId; text: string}> = ({id, text}) => {
  switch (id) {
    case '01_hook':
      return <Scene1Hook />;
    default:
      return <PlaceholderScene label={text} />;
  }
};

export const MainVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      {SCHEDULE.map((scene) => {
        const audioPath = manifest[scene.id];
        return (
          <Sequence
            key={scene.id}
            from={scene.startFrame}
            durationInFrames={scene.endFrame - scene.startFrame}
            name={scene.id}
          >
            <SceneFor id={scene.id} text={scene.text} />
            {audioPath ? <Audio src={staticFile(audioPath)} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
