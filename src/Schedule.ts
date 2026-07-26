import {FPS} from './theme';

// Real narration durations, measured via ffprobe against the ElevenLabs
// "Adam" audio files in public/audio (see scripts/measure-audio.mjs).
// Frame counts are exact (30fps); do not hand-edit without re-measuring.
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

const s = (seconds: number) => Math.round(seconds * FPS);

// [id, text, measuredVoFrames, holdAfterFrames]
const RAW: [SegmentId, string, number, number][] = [
  [
    '01_hook',
    'Someone built an AI to read two point six million cancer studies. It came back with a number nobody wanted.',
    208,
    s(5),
  ],
  [
    '02_number',
    'Two hundred and fifty thousand cancer papers — roughly one in ten — written in a way that matches papers already retracted for being fabricated.',
    294,
    s(6),
  ],
  [
    '03_scope',
    'Not one journal, not one country. Nobody found these by reading them — they found them by noticing they all sounded the same.',
    241,
    s(6),
  ],
  [
    '04_papermill_def',
    'A paper mill is a company that sells finished research papers with your name on it, or sells you an author slot on someone else’s.',
    219,
    s(4),
  ],
  [
    '05_demand',
    'The demand comes from researchers who need publications to keep their careers — no papers, no career.',
    219,
    s(4),
  ],
  [
    '06_supply',
    'So the supply became industrial: 400,000+ suspected papers in 20 years, one publisher retracting 11,000 papers and shutting 19 journals.',
    321,
    s(9),
  ],
  [
    '07_method',
    'Nobody could read 2.6 million papers by hand, so researchers trained a language model to spot the shared ‘template fingerprint’ paper mills leave behind.',
    352,
    s(8),
  ],
  [
    '08_accuracy',
    'It hit 91% accuracy and flagged 9.87% of the literature — a share that’s growing, and growing fastest inside the top 10% of journals by impact factor.',
    382,
    s(10),
  ],
  [
    '09_country',
    'Over 170,000 flagged papers came from one country’s institutions — not because its scientists are worse, but because its promotion system turned publication into a currency.',
    369,
    s(8),
  ],
  [
    '10_twist',
    'Then the twist: Nature reported these flagged papers get MORE citations than legitimate ones, because fabricated data is clean — no messy nulls or contradictions — so real trials and real funding get built on top of it.',
    502,
    s(20),
  ],
  [
    '11_caveat',
    'And none of it is proven fake. Flagging is a screen, not a verdict — every paper still needs a human expert.',
    212,
    s(5),
  ],
  [
    '12_scale',
    'We can detect this at the scale of millions. We can only verify it one paper at a time.',
    183,
    s(5),
  ],
  [
    '13_closer',
    'So — who checks 250,000 papers? And what happens to the ones nobody gets to?',
    208,
    s(12),
  ],
];

export const SEGMENTS = RAW.map(([id, text, durationInFrames, holdAfter]) => ({
  id,
  text,
  audioFile: `${id}.mp3`,
  durationInFrames,
  holdAfter,
}));

export type Segment = (typeof SEGMENTS)[number];

export const OPENING_TITLE_FRAMES = s(3);

// Interstitial "chapter bumper" cards — short black/navy title cards that
// break the explainer into sections, Vox-style.
export type InterstitialId = 'how' | 'method' | 'twist' | 'caveat';
export const INTERSTITIALS: Record<
  InterstitialId,
  {label: string; durationInFrames: number; before: SegmentId; silent?: boolean}
> = {
  how: {label: 'How This Happened', durationInFrames: s(2.5), before: '04_papermill_def'},
  method: {label: 'The Method', durationInFrames: s(2.5), before: '07_method'},
  // This is also the full audio drop: no narration, no drone, just the card.
  twist: {label: 'The Twist', durationInFrames: s(3), before: '10_twist', silent: true},
  caveat: {label: 'The Caveat', durationInFrames: s(2.5), before: '11_caveat'},
};

export type TimelineBlock =
  | {kind: 'title'; startFrame: number; endFrame: number}
  | {
      kind: 'interstitial';
      id: InterstitialId;
      label: string;
      silent: boolean;
      startFrame: number;
      endFrame: number;
    }
  | {
      kind: 'segment';
      segment: Segment;
      startFrame: number;
      voEndFrame: number;
      endFrame: number;
    };

const interstitialByBefore = Object.fromEntries(
  (Object.entries(INTERSTITIALS) as [InterstitialId, (typeof INTERSTITIALS)[InterstitialId]][]).map(
    ([id, v]) => [v.before, {id, ...v}],
  ),
) as Record<SegmentId, {id: InterstitialId; label: string; durationInFrames: number; silent?: boolean}>;

export const buildTimeline = (): TimelineBlock[] => {
  const blocks: TimelineBlock[] = [];
  let cursor = 0;

  blocks.push({kind: 'title', startFrame: cursor, endFrame: cursor + OPENING_TITLE_FRAMES});
  cursor += OPENING_TITLE_FRAMES;

  for (const seg of SEGMENTS) {
    const bumper = interstitialByBefore[seg.id];
    if (bumper) {
      const start = cursor;
      const end = start + bumper.durationInFrames;
      blocks.push({
        kind: 'interstitial',
        id: bumper.id,
        label: bumper.label,
        silent: Boolean(bumper.silent),
        startFrame: start,
        endFrame: end,
      });
      cursor = end;
    }

    const start = cursor;
    const voEnd = start + seg.durationInFrames;
    const end = voEnd + seg.holdAfter;
    blocks.push({kind: 'segment', segment: seg, startFrame: start, voEndFrame: voEnd, endFrame: end});
    cursor = end;
  }

  return blocks;
};

export const TIMELINE = buildTimeline();
export const TOTAL_FRAMES = TIMELINE[TIMELINE.length - 1].endFrame;
