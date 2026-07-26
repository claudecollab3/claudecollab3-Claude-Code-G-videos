/**
 * Dev-time guard for the theme's hard rule: `flagged` red and `legit` teal
 * must never appear in the same frame without a visible text label telling
 * them apart. Call from any scene that renders both colors at once.
 */
export const assertLabeledDualColor = (hasFlaggedLabel: boolean, hasLegitLabel: boolean) => {
  if (process.env.NODE_ENV === "production") return;
  if (!hasFlaggedLabel || !hasLegitLabel) {
    throw new Error(
      "Theme rule violated: flagged (red) and legit (teal) rendered together without a distinguishing label for both.",
    );
  }
};
