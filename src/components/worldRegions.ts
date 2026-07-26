// Rough, deliberately non-cartographic continent blobs — enough to read as
// "a world map" at a glance without needing real geo data.
export type Region = {
  id: string;
  cx: number;
  cy: number;
  rx: number;
  ry: number;
};

export const REGIONS: Region[] = [
  {id: 'na', cx: 470, cy: 360, rx: 160, ry: 110},
  {id: 'sa', cx: 590, cy: 680, rx: 90, ry: 150},
  {id: 'eu', cx: 960, cy: 300, rx: 70, ry: 60},
  {id: 'af', cx: 990, cy: 540, rx: 105, ry: 155},
  {id: 'as', cx: 1260, cy: 370, rx: 220, ry: 140},
  {id: 'au', cx: 1520, cy: 700, rx: 80, ry: 50},
];

export type Dot = {x: number; y: number; region: string; seed: number};

const mulberry32 = (seed: number) => {
  let a = seed;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

export const generateDots = (perRegion: number): Dot[] => {
  const rand = mulberry32(42);
  const dots: Dot[] = [];
  for (const region of REGIONS) {
    let placed = 0;
    let attempts = 0;
    while (placed < perRegion && attempts < perRegion * 8) {
      attempts++;
      const angle = rand() * Math.PI * 2;
      const r = Math.sqrt(rand());
      const x = region.cx + Math.cos(angle) * region.rx * r;
      const y = region.cy + Math.sin(angle) * region.ry * r;
      dots.push({x, y, region: region.id, seed: Math.floor(rand() * 1e6)});
      placed++;
    }
  }
  return dots;
};
