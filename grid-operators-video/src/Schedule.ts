import {FPS} from './theme';

// Placeholder word-count-based estimates (frames @ 30fps). Overwritten with
// real ffprobe-measured durations once the ElevenLabs "Sully" narration
// audio is available.
export type SceneId =
  | '01_hook'
  | '02_contradiction'
  | '03_grid_stress'
  | '04_datacenters_arrive'
  | '05_contract'
  | '06_villain_hero'
  | '07_spreading'
  | '08_ending';

const s = (seconds: number) => Math.round(seconds * FPS);

export type Scene = {
  id: SceneId;
  text: string;
  audioFile: string;
  durationInFrames: number;
  holdAfter: number;
};

const RAW: [SceneId, string, number, number][] = [
  ['01_hook', 'Every AI data center needs power — endless power.', s(3.8), s(0.4)],
  [
    '02_contradiction',
    'So why is the electric grid now paying them to turn off?',
    s(5.0),
    s(0.4),
  ],
  [
    '03_grid_stress',
    "For decades, the grid's biggest problem was demand it couldn't control. A heatwave hits, and there's no time to react.",
    s(8.3),
    s(0.4),
  ],
  [
    '04_datacenters_arrive',
    'Then data centers arrived. Massive, power-hungry — and unlike a hospital, or a factory, an AI training run can pause.',
    s(7.0),
    s(0.4),
  ],
  [
    '05_contract',
    'So grid operators started signing contracts: when the grid is stressed, the data center powers down, and gets paid for it.',
    s(8.3),
    s(0.4),
  ],
  [
    '06_villain_hero',
    "The industry's biggest energy villain just became the grid's shock absorber.",
    s(4.5),
    s(0.4),
  ],
  [
    '07_spreading',
    "It's already happening in Texas, Ireland, and Singapore — and it's spreading fast.",
    s(5.8),
    s(0.4),
  ],
  [
    '08_ending',
    'Which means the next blackout might not be prevented by a power plant. It might be prevented by an AI... just pausing.',
    s(7.0),
    s(1.5),
  ],
];

export const SCENES: Scene[] = RAW.map(([id, text, durationInFrames, holdAfter]) => ({
  id,
  text,
  audioFile: `${id}.mp3`,
  durationInFrames,
  holdAfter,
}));

export type ScheduledScene = Scene & {
  startFrame: number;
  voEndFrame: number;
  endFrame: number;
};

export const buildSchedule = (): ScheduledScene[] => {
  let cursor = 0;
  const out: ScheduledScene[] = [];
  for (const scene of SCENES) {
    const startFrame = cursor;
    const voEndFrame = startFrame + scene.durationInFrames;
    const endFrame = voEndFrame + scene.holdAfter;
    out.push({...scene, startFrame, voEndFrame, endFrame});
    cursor = endFrame;
  }
  return out;
};

export const SCHEDULE = buildSchedule();
export const TOTAL_FRAMES = SCHEDULE[SCHEDULE.length - 1].endFrame;
