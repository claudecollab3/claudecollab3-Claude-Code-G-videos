import {mulberry32} from './random';

/** A jagged lightning-bolt ribbon strip, as a filled polygon path. */
export const lightningBoltPath = (w: number, h: number, seed: number): string => {
  const rand = mulberry32(seed);
  const segments = 6;
  const midX = w * 0.5;
  const left: [number, number][] = [];
  const right: [number, number][] = [];

  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const y = t * h;
    const wobble = (rand() - 0.5) * w * 0.55;
    const cx = midX + Math.sin(t * Math.PI * 2.4 + seed) * w * 0.2 + wobble * 0.35;
    const half = w * (0.05 + rand() * 0.02);
    left.push([cx - half, y]);
    right.push([cx + half, y]);
  }

  const path =
    `M ${left[0][0].toFixed(1)},${left[0][1].toFixed(1)} ` +
    left
      .slice(1)
      .map(([x, y]) => `L ${x.toFixed(1)},${y.toFixed(1)}`)
      .join(' ') +
    ' ' +
    right
      .slice()
      .reverse()
      .map(([x, y]) => `L ${x.toFixed(1)},${y.toFixed(1)}`)
      .join(' ') +
    ' Z';
  return path;
};
