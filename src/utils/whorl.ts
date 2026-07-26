/** Procedural fingerprint-whorl path generator: concentric ridge lines built
 * from a perturbed spiral, so SC-13's hero visual is generated code, not an
 * asset. Each ridge is offset in radius from the last, and all share the
 * same low-frequency perturbation so they read as flowing ridge lines
 * rather than perfect circles. */
export type WhorlRidge = { d: string; approxLength: number };

export const buildWhorlRidge = (
  centerX: number,
  centerY: number,
  baseRadius: number,
  turns: number,
  points = 220,
  perturbAmp = 10,
  perturbFreq = 3.4,
  phase = 0,
): WhorlRidge => {
  let d = "";
  let approxLength = 0;
  let prevX = centerX;
  let prevY = centerY;
  for (let i = 0; i <= points; i++) {
    const t = i / points;
    const theta = t * Math.PI * 2 * turns;
    const r =
      baseRadius +
      Math.sin(theta * perturbFreq + phase) * perturbAmp * (0.4 + 0.6 * t);
    const x = centerX + Math.cos(theta) * r * (1 - t * 0.02);
    const y = centerY + Math.sin(theta) * r * (1 - t * 0.02);
    d += i === 0 ? `M${x.toFixed(2)},${y.toFixed(2)}` : ` L${x.toFixed(2)},${y.toFixed(2)}`;
    if (i > 0) approxLength += Math.hypot(x - prevX, y - prevY);
    prevX = x;
    prevY = y;
  }
  return { d, approxLength };
};

export const buildWhorlRidges = (
  centerX: number,
  centerY: number,
  count: number,
  minRadius: number,
  radiusStep: number,
): WhorlRidge[] =>
  Array.from({ length: count }).map((_, i) =>
    buildWhorlRidge(
      centerX,
      centerY,
      minRadius + i * radiusStep,
      2.4 + (i % 3) * 0.15,
      220,
      8 + (i % 4) * 2,
      3.2 + (i % 5) * 0.3,
      i * 0.4,
    ),
  );
