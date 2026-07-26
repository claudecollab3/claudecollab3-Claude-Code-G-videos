import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { COLORS } from "./constants/theme";
import { getSceneComponent } from "./SceneRegistry";
import { resolveTimeline } from "./utils/timeline";
import { CaptionsTrack } from "./components/CaptionsTrack";
import { buildCaptionCards } from "./utils/captions";

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const mainVideoDurationInFrames = () => resolveTimeline(FPS).totalDurationInFrames;

export const MainVideo: React.FC = () => {
  const { acts, scenes } = resolveTimeline(FPS);

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {acts.map((act) => (
        <Sequence key={act.id} from={act.startFrame} durationInFrames={act.durationInFrames}>
          <Audio src={staticFile(act.file)} />
        </Sequence>
      ))}
      {scenes.map((scene) => {
        const Scene = getSceneComponent(scene.id);
        return (
          <Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.durationInFrames}>
            <Scene aspect="landscape" />
          </Sequence>
        );
      })}
      <CaptionsTrack aspect="landscape" cards={buildCaptionCards(FPS)} />
    </AbsoluteFill>
  );
};
