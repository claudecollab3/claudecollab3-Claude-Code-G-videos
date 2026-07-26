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
  let openBookendEnd = 0;
  let closeBookendStart = Infinity;
  const sceneSequences = SHORTS_SCENE_PLAN.map((entry, i) => {
    const startFrame = cursorFrames;
    const durationInFrames = Math.round(entry.seconds * SHORTS_FPS);
    cursorFrames += durationInFrames;
    if (entry.id === "LOOP-BOOKEND") {
      if (i === 0) openBookendEnd = startFrame + durationInFrames;
      else closeBookendStart = startFrame;
    }
    const Scene = getSceneComponent(entry.id);
    return (
      <Sequence key={`${entry.id}-${i}`} from={startFrame} durationInFrames={durationInFrames}>
        <Scene aspect="vertical" />
      </Sequence>
    );
  });

  // Keep both loop-bookend instances caption-free so the very first frame and
  // the very last frame stay pixel-identical (the hard-loop requirement).
  const captionCards = buildShortsCaptionCards(SHORTS_FPS).filter(
    (card) => card.startFrame >= openBookendEnd && card.startFrame + card.durationInFrames <= closeBookendStart,
  );

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
      <CaptionsTrack aspect="vertical" cards={captionCards} />
    </AbsoluteFill>
  );
};
