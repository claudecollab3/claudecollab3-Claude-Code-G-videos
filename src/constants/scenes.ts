export type SceneSpec = {
  id: string;
  actId: string;
  /** Nominal seconds from the storyboard, relative to the start of the act. */
  localStart: number;
  localEnd: number;
};

/** Nominal (storyboard-estimate) act durations these localStart/End are relative to. */
export const NOMINAL_ACT_DURATIONS: Record<string, number> = {
  "act-01": 5,
  "act-02": 25,
  "act-03": 60,
  "act-04": 80,
  "act-05": 40,
  "act-06": 25,
  "act-07": 5,
};

export const SCENES: SceneSpec[] = [
  { id: "SC-01", actId: "act-01", localStart: 0, localEnd: 3 },
  { id: "SC-02", actId: "act-01", localStart: 3, localEnd: 5 },
  { id: "SC-03", actId: "act-02", localStart: 0, localEnd: 7 },
  { id: "SC-04", actId: "act-02", localStart: 7, localEnd: 13 },
  { id: "SC-05", actId: "act-02", localStart: 13, localEnd: 25 },
  { id: "SC-06", actId: "act-03", localStart: 0, localEnd: 10 },
  { id: "SC-07", actId: "act-03", localStart: 10, localEnd: 22 },
  { id: "SC-08", actId: "act-03", localStart: 22, localEnd: 34 },
  { id: "SC-09", actId: "act-03", localStart: 34, localEnd: 44 },
  { id: "SC-10", actId: "act-03", localStart: 44, localEnd: 54 },
  { id: "SC-11", actId: "act-03", localStart: 54, localEnd: 60 },
  { id: "SC-12", actId: "act-04", localStart: 0, localEnd: 12 },
  { id: "SC-13", actId: "act-04", localStart: 12, localEnd: 24 },
  { id: "SC-14", actId: "act-04", localStart: 24, localEnd: 36 },
  { id: "SC-15", actId: "act-04", localStart: 36, localEnd: 44 },
  { id: "SC-16", actId: "act-04", localStart: 44, localEnd: 54 },
  { id: "SC-17", actId: "act-04", localStart: 54, localEnd: 64 },
  { id: "SC-18", actId: "act-04", localStart: 64, localEnd: 80 },
  { id: "SC-19", actId: "act-05", localStart: 0, localEnd: 10 },
  { id: "SC-20", actId: "act-05", localStart: 10, localEnd: 24 },
  { id: "SC-21", actId: "act-05", localStart: 24, localEnd: 40 },
  { id: "SC-22", actId: "act-06", localStart: 0, localEnd: 14 },
  { id: "SC-23", actId: "act-06", localStart: 14, localEnd: 25 },
  { id: "SC-24", actId: "act-07", localStart: 0, localEnd: 5 },
];
