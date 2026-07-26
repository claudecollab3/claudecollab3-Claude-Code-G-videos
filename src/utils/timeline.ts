import timings from "../../public/audio/timings.json";
import { NOMINAL_ACT_DURATIONS, SCENES } from "../constants/scenes";

export type ResolvedScene = {
  id: string;
  actId: string;
  startFrame: number;
  durationInFrames: number;
};

export type ResolvedAct = {
  id: string;
  startFrame: number;
  durationInFrames: number;
  file: string;
};

/**
 * Scales each scene's nominal (storyboard-estimate) local timing by the
 * ratio of the act's real rendered VO duration to its nominal duration, so
 * scene cuts track actual narration length instead of the 240s estimate.
 */
export const resolveTimeline = (fps: number) => {
  const actById = new Map(timings.acts.map((a) => [a.id, a]));

  const acts: ResolvedAct[] = timings.acts.map((a) => ({
    id: a.id,
    startFrame: Math.round(a.startSeconds * fps),
    durationInFrames: Math.round(a.durationSeconds * fps),
    file: a.file,
  }));

  const scenes: ResolvedScene[] = SCENES.map((scene) => {
    const act = actById.get(scene.actId);
    if (!act) throw new Error(`No timing manifest entry for act ${scene.actId}`);
    const nominalActDuration = NOMINAL_ACT_DURATIONS[scene.actId];
    const scale = act.durationSeconds / nominalActDuration;
    const startSeconds = act.startSeconds + scene.localStart * scale;
    const endSeconds = act.startSeconds + scene.localEnd * scale;
    const startFrame = Math.round(startSeconds * fps);
    const endFrame = Math.round(endSeconds * fps);
    return {
      id: scene.id,
      actId: scene.actId,
      startFrame,
      durationInFrames: Math.max(1, endFrame - startFrame),
    };
  });

  const totalDurationInFrames = Math.round(timings.totalSeconds * fps);

  return { acts, scenes, totalDurationInFrames };
};

export const getScene = (id: string, fps: number): ResolvedScene => {
  const { scenes } = resolveTimeline(fps);
  const scene = scenes.find((s) => s.id === id);
  if (!scene) throw new Error(`Unknown scene ${id}`);
  return scene;
};
