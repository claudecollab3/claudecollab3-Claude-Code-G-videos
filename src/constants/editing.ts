/** Cut pacing targets, in seconds between cuts, by act. */
export const CUT_PACE = {
  act1_2: [1.2, 1.8] as [number, number],
  act3: [2.5, 3.5] as [number, number],
  act4: 1.5,
  act5_orbit: 8, // single unbroken shot at SC-20
  act5_rest: 1.0,
  act6_7: [3, 4] as [number, number],
};

/** The only two whip pans, the only match cut, the only slow fade. */
export const SPECIAL_TRANSITIONS = {
  whipPans: ["SC-05->SC-06", "SC-12->SC-13"],
  matchCuts: ["SC-01(person)->SC-12(wireframe)"],
  slowFades: ["SC-21->SC-22"],
};

/** SC-21 is the only permitted real-footage insert in the whole video. */
export const STOCK_FOOTAGE_ALLOWLIST = ["SC-21-microscope"];
