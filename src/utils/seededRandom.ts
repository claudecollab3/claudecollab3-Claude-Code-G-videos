/** Deterministic PRNG so per-item jitter is stable across frames/renders. */
export const seededRandom = (seed: number) => {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
};

export const jitterFor = (index: number, salt = 0) => {
  const rand = seededRandom(index * 9973 + salt * 7919 + 1);
  return { x: rand(), y: rand(), r: rand() };
};
