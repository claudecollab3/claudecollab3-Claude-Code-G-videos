import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {SCHEDULE, OPENING_TITLE_FRAMES, SegmentId} from './Schedule';
import {OpeningTitle} from './scenes/OpeningTitle';
import {PaperColumnScene} from './scenes/PaperColumnScene';
import {PlaceholderScene} from './scenes/PlaceholderScene';
import {Caption} from './components/Caption';
import audioManifest from './audioManifest.json';
import {COLORS} from './theme';

const manifest = audioManifest as Record<string, string>;

const SceneFor: React.FC<{id: SegmentId; text: string}> = ({id, text}) => {
  switch (id) {
    case '01_hook':
      return (
        <>
          <PaperColumnScene />
          <Caption text={text} />
        </>
      );
    default:
      return <PlaceholderScene label={id} text={text} />;
  }
};

export const MainVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <Sequence from={0} durationInFrames={OPENING_TITLE_FRAMES} name="opening-title">
        <OpeningTitle />
      </Sequence>

      {SCHEDULE.map((seg) => {
        const audioPath = manifest[seg.id];
        return (
          <Sequence
            key={seg.id}
            from={seg.startFrame}
            durationInFrames={seg.sceneEndFrame - seg.startFrame}
            name={seg.id}
          >
            <SceneFor id={seg.id} text={seg.text} />
            {audioPath ? <Audio src={staticFile(audioPath)} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
