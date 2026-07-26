import {FPS} from './theme';

// Placeholder word-count-based estimates (frames @ 30fps).
// These get overwritten with real ffprobe-measured durations once
// the ElevenLabs narration audio is available (see scripts/apply-audio-durations.ts).
export type SegmentId =
  | '01_hook'
  | '02_number'
  | '03_scope'
  | '04_papermill_def'
  | '05_demand'
  | '06_supply'
  | '07_method'
  | '08_accuracy'
  | '09_country'
  | '10_twist'
  | '11_caveat'
  | '12_scale'
  | '13_closer';

export type Segment = {
  id: SegmentId;
  text: string;
  audioFile: string;
  durationInFrames: number;
  // Extra hold time after the VO line ends, for the visual to breathe (frames).
  holdAfter: number;
};

const s = (seconds: number) => Math.round(seconds * FPS);

export const SEGMENTS: Segment[] = [
  {
    id: '01_hook',
    text: 'Someone built an AI to read two point six million cancer studies. It came back with a number nobody wanted.',
    audioFile: '01_hook.mp3',
    durationInFrames: s(7.5),
    holdAfter: s(0.5),
  },
  {
    id: '02_number',
    text: 'Two hundred and fifty thousand cancer papers — roughly one in ten — written in a way that matches papers already retracted for being fabricated.',
    audioFile: '02_number.mp3',
    durationInFrames: s(9.5),
    holdAfter: s(1),
  },
  {
    id: '03_scope',
    text: 'Not one journal, not one country. Nobody found these by reading them — they found them by noticing they all sounded the same.',
    audioFile: '03_scope.mp3',
    durationInFrames: s(8.5),
    holdAfter: s(0.5),
  },
  {
    id: '04_papermill_def',
    text: 'A paper mill is a company that sells finished research papers with your name on it, or sells you an author slot on someone else’s.',
    audioFile: '04_papermill_def.mp3',
    durationInFrames: s(9),
    holdAfter: s(0.5),
  },
  {
    id: '05_demand',
    text: 'The demand comes from researchers who need publications to keep their careers — no papers, no career.',
    audioFile: '05_demand.mp3',
    durationInFrames: s(6.5),
    holdAfter: s(0.5),
  },
  {
    id: '06_supply',
    text: 'So the supply became industrial: 400,000+ suspected papers in 20 years, one publisher retracting 11,000 papers and shutting 19 journals.',
    audioFile: '06_supply.mp3',
    durationInFrames: s(10),
    holdAfter: s(1),
  },
  {
    id: '07_method',
    text: 'Nobody could read 2.6 million papers by hand, so researchers trained a language model to spot the shared ‘template fingerprint’ paper mills leave behind.',
    audioFile: '07_method.mp3',
    durationInFrames: s(10.5),
    holdAfter: s(0.5),
  },
  {
    id: '08_accuracy',
    text: 'It hit 91% accuracy and flagged 9.87% of the literature — a share that’s growing, and growing fastest inside the top 10% of journals by impact factor.',
    audioFile: '08_accuracy.mp3',
    durationInFrames: s(11.5),
    holdAfter: s(1),
  },
  {
    id: '09_country',
    text: 'Over 170,000 flagged papers came from one country’s institutions — not because its scientists are worse, but because its promotion system turned publication into a currency.',
    audioFile: '09_country.mp3',
    durationInFrames: s(10.5),
    holdAfter: s(1.5),
  },
  {
    id: '10_twist',
    text: 'Then the twist: Nature reported these flagged papers get MORE citations than legitimate ones, because fabricated data is clean — no messy nulls or contradictions — so real trials and real funding get built on top of it.',
    audioFile: '10_twist.mp3',
    durationInFrames: s(13),
    holdAfter: s(2),
  },
  {
    id: '11_caveat',
    text: 'And none of it is proven fake. Flagging is a screen, not a verdict — every paper still needs a human expert.',
    audioFile: '11_caveat.mp3',
    durationInFrames: s(7.5),
    holdAfter: s(0.5),
  },
  {
    id: '12_scale',
    text: 'We can detect this at the scale of millions. We can only verify it one paper at a time.',
    audioFile: '12_scale.mp3',
    durationInFrames: s(6.5),
    holdAfter: s(0.5),
  },
  {
    id: '13_closer',
    text: 'So — who checks 250,000 papers? And what happens to the ones nobody gets to?',
    audioFile: '13_closer.mp3',
    durationInFrames: s(6.5),
    holdAfter: s(3),
  },
];

// Silence gap before the twist (full audio drop).
export const DROP_GAP_FRAMES = s(1.5);
export const DROP_BEFORE: SegmentId = '10_twist';

export const OPENING_TITLE_FRAMES = s(3);

export type ScheduledSegment = Segment & {
  startFrame: number;
  endFrame: number; // end of VO
  sceneEndFrame: number; // end of hold (scene cut point)
};

export const buildSchedule = (): ScheduledSegment[] => {
  let cursor = OPENING_TITLE_FRAMES;
  const out: ScheduledSegment[] = [];
  for (const seg of SEGMENTS) {
    if (seg.id === DROP_BEFORE) {
      cursor += DROP_GAP_FRAMES;
    }
    const startFrame = cursor;
    const endFrame = startFrame + seg.durationInFrames;
    const sceneEndFrame = endFrame + seg.holdAfter;
    out.push({...seg, startFrame, endFrame, sceneEndFrame});
    cursor = sceneEndFrame;
  }
  return out;
};

export const SCHEDULE = buildSchedule();
export const TOTAL_FRAMES = SCHEDULE[SCHEDULE.length - 1].sceneEndFrame + OPENING_TITLE_FRAMES;
