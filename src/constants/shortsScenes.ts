/** Fixed visual cut plan for ShortsCut — hand-authored (not scaled from VO
 * timing, unlike MainVideo) since the shorts cutdown reorders/condenses
 * scenes rather than following the act structure 1:1. Seconds sum to 58.0. */
export const SHORTS_SCENE_PLAN: { id: string; seconds: number }[] = [
  { id: "LOOP-BOOKEND", seconds: 0.6 },
  { id: "SC-01", seconds: 2.4 },
  { id: "SC-03", seconds: 8 },
  { id: "SC-07", seconds: 10 },
  { id: "SC-13", seconds: 8 },
  { id: "SC-16", seconds: 8 },
  { id: "SC-19", seconds: 3 },
  { id: "SC-20", seconds: 9 },
  { id: "SC-22", seconds: 6 },
  { id: "SC-24", seconds: 2.4 },
  { id: "LOOP-BOOKEND", seconds: 0.6 },
];

export const SHORTS_TOTAL_SECONDS = SHORTS_SCENE_PLAN.reduce((s, x) => s + x.seconds, 0);
