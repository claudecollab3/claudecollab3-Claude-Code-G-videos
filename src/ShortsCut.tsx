import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import shortsTimings from "../public/audio/shorts/timings.json";
import { COLORS } from "./constants/theme";
import { SHORTS_SCENE_PLAN, SHORTS_TOTAL_SECONDS } from "./constants/shortsScenes";
import { getSceneComponent } from "./SceneRegistry";
import { CaptionsTrack } from "./components/CaptionsTrack";
import { buildShortsCaptionCards } from "./utils/shortsCaptions";

export const SHORTS_FPS = 30;
export const SHORTS_WIDTH = 1080;
export const SHORTS_HEIGHT = 1920;

export const shortsDurationInFrames = () => Math.round(SHORTS_TOTAL_SECONDS * SHORTS_FPS);

export const ShortsCut: React.FC = () => {
  let cursorFrames = 0;
  const sceneSequences = SHORTS_SCENE_PLAN.map((entry, i) => {
    const startFrame = cursorFrames;
    const durationInFrames = Math.round(entry.seconds * SHORTS_FPS);
    cursorFrames += durationInFrames;
    const Scene = getSceneComponent(entry.id);
    return (
      <Sequence key={`${entry.id}-${i}`} from={startFrame} durationInFrames={durationInFrames}>
        <Scene aspect="vertical" />
      </Sequence>
    );
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {shortsTimings.acts.map((act) => (
        <Sequence
          key={act.id}
          from={Math.round(act.startSeconds * SHORTS_FPS)}
          durationInFrames={Math.round(act.durationSeconds * SHORTS_FPS)}
        >
          <Audio src={staticFile(act.file)} />
        </Sequence>
      ))}
      {sceneSequences}
      <CaptionsTrack aspect="vertical" cards={buildShortsCaptionCards(SHORTS_FPS)} />
    </AbsoluteFill>
  );
};
