import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {TIMELINE, SegmentId} from './Schedule';
import {OpeningTitle} from './scenes/OpeningTitle';
import {Interstitial} from './scenes/Interstitial';
import {PaperColumnScene} from './scenes/PaperColumnScene';
import {GridFlipScene} from './scenes/GridFlipScene';
import {WorldMapScene} from './scenes/WorldMapScene';
import {PaperMillDefScene} from './scenes/PaperMillDefScene';
import {DemandScene} from './scenes/DemandScene';
import {StatBlockScene} from './scenes/StatBlockScene';
import {FingerprintScene} from './scenes/FingerprintScene';
import {LineChartScene} from './scenes/LineChartScene';
import {CitationNetworkScene} from './scenes/CitationNetworkScene';
import {CalloutScene} from './scenes/CalloutScene';
import {SplitStatScene} from './scenes/SplitStatScene';
import {ClosingScene} from './scenes/ClosingScene';
import {Caption} from './components/Caption';
import {AmbientDrone} from './components/AmbientDrone';
import audioManifest from './audioManifest.json';
import {COLORS} from './theme';

const manifest = audioManifest as Record<string, string>;

const SceneFor: React.FC<{id: SegmentId; text: string; voDurationInFrames: number}> = ({
  id,
  text,
  voDurationInFrames,
}) => {
  switch (id) {
    case '01_hook':
      return (
        <>
          <PaperColumnScene />
          <Caption text={text} />
        </>
      );
    case '02_number':
      return (
        <>
          <GridFlipScene />
          <Caption text={text} color={COLORS.textDim} />
        </>
      );
    case '03_scope':
      return (
        <>
          <WorldMapScene variant="scope" />
          <Caption text={text} />
        </>
      );
    case '04_papermill_def':
      return <PaperMillDefScene voDurationInFrames={voDurationInFrames} />;
    case '05_demand':
      return <DemandScene voDurationInFrames={voDurationInFrames} />;
    case '06_supply':
      return (
        <>
          <StatBlockScene />
          <Caption text={text} color={COLORS.textDim} />
        </>
      );
    case '07_method':
      return (
        <>
          <FingerprintScene />
          <Caption text={text} color={COLORS.textDim} />
        </>
      );
    case '08_accuracy':
      return <LineChartScene />;
    case '09_country':
      return <WorldMapScene variant="country" />;
    case '10_twist':
      return <CitationNetworkScene />;
    case '11_caveat':
      return <CalloutScene voDurationInFrames={voDurationInFrames} />;
    case '12_scale':
      return (
        <>
          <SplitStatScene />
          <Caption text={text} color={COLORS.textDim} />
        </>
      );
    case '13_closer':
      return <ClosingScene />;
    default:
      return null;
  }
};

export const MainVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <AmbientDrone />

      {TIMELINE.map((block) => {
        if (block.kind === 'title') {
          return (
            <Sequence key="title" from={block.startFrame} durationInFrames={block.endFrame - block.startFrame} name="opening-title">
              <OpeningTitle />
            </Sequence>
          );
        }
        if (block.kind === 'interstitial') {
          return (
            <Sequence
              key={`bumper-${block.id}`}
              from={block.startFrame}
              durationInFrames={block.endFrame - block.startFrame}
              name={`bumper-${block.id}`}
            >
              <Interstitial label={block.label} silent={block.silent} />
            </Sequence>
          );
        }
        const seg = block.segment;
        const audioPath = manifest[seg.id];
        return (
          <Sequence
            key={seg.id}
            from={block.startFrame}
            durationInFrames={block.endFrame - block.startFrame}
            name={seg.id}
          >
            <SceneFor id={seg.id} text={seg.text} voDurationInFrames={seg.durationInFrames} />
            {audioPath ? <Audio src={staticFile(audioPath)} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
