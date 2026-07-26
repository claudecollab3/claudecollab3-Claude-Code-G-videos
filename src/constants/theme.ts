import { LOADED_FONTS } from "./fonts";

export const COLORS = {
  bg: "#0A0E1A", // deep navy base
  text: "#F2F0EB", // bone white
  flagged: "#E63946", // alert red — ONLY for flagged/fraud data, never decorative
  legit: "#4ECDC4", // teal — verified/legitimate data
  uncertain: "#FFB627", // amber — hedges, "we don't know", sympathy beats
} as const;

export const FONTS = {
  numeral: LOADED_FONTS.numeral, // condensed grotesque, for all counters
  body: LOADED_FONTS.body, // humanist sans, for all VO-synced text
} as const;

/**
 * Enforced rule: never render `flagged` red and `legit` teal in the same
 * frame without a visible text label distinguishing them. Components that
 * mix these two colors (e.g. SC-15, SC-20, SC-21) must pass a `label` prop
 * for each color use — see `assertLabeledDualColor` in
 * `src/constants/colorRule.ts`.
 */
export const DUAL_COLOR_PAIR = [COLORS.flagged, COLORS.legit] as const;
