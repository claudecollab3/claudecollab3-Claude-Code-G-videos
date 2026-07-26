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

export type GraphNode = {
  id: number;
  x: number;
  y: number;
  flagged: boolean;
  birthFrame: number;
  radius: number;
};

export type GraphEdge = {
  a: number;
  b: number;
  birthFrame: number;
};

const WIDTH = 2600;
const HEIGHT = 1500;

export const generateCitationGraph = (
  nodeCount: number,
  totalGrowthFrames: number,
): {nodes: GraphNode[]; edges: GraphEdge[]} => {
  const rand = mulberry32(1337);
  const nodes: GraphNode[] = [];

  for (let i = 0; i < nodeCount; i++) {
    // Roughly 55% flagged overall, but flagged nodes are heavily weighted
    // toward the back half of the timeline so they visibly "multiply faster".
    const flagged = rand() < 0.55;
    const t = i / (nodeCount - 1);
    const skew = flagged ? Math.pow(t, 0.55) : Math.pow(t, 1.4);
    const birthFrame = Math.round(skew * totalGrowthFrames);

    nodes.push({
      id: i,
      x: WIDTH / 2 + (rand() - 0.5) * WIDTH * 0.92,
      y: HEIGHT / 2 + (rand() - 0.5) * HEIGHT * 0.92,
      flagged,
      birthFrame,
      radius: flagged ? 8 + rand() * 6 : 6 + rand() * 4,
    });
  }

  // k-nearest-neighbour edges for a citation-network look.
  const edges: GraphEdge[] = [];
  const K = 3;
  for (const node of nodes) {
    const distances = nodes
      .filter((n) => n.id !== node.id)
      .map((n) => ({id: n.id, d: Math.hypot(n.x - node.x, n.y - node.y)}))
      .sort((x, y) => x.d - y.d)
      .slice(0, K);
    for (const near of distances) {
      const exists = edges.some(
        (e) => (e.a === node.id && e.b === near.id) || (e.a === near.id && e.b === node.id),
      );
      if (!exists) {
        const other = nodes[near.id];
        edges.push({a: node.id, b: near.id, birthFrame: Math.max(node.birthFrame, other.birthFrame)});
      }
    }
  }

  // Simple force relaxation: repel all pairs slightly, pull edges together.
  const ITER = 60;
  for (let iter = 0; iter < ITER; iter++) {
    const forces = nodes.map(() => ({fx: 0, fy: 0}));
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const distSq = Math.max(dx * dx + dy * dy, 400);
        const force = 1800 / distSq;
        const fx = (dx / Math.sqrt(distSq)) * force;
        const fy = (dy / Math.sqrt(distSq)) * force;
        forces[i].fx -= fx;
        forces[i].fy -= fy;
        forces[j].fx += fx;
        forces[j].fy += fy;
      }
    }
    for (const edge of edges) {
      const na = nodes[edge.a];
      const nb = nodes[edge.b];
      const dx = nb.x - na.x;
      const dy = nb.y - na.y;
      const dist = Math.hypot(dx, dy) || 1;
      const target = 140;
      const pull = (dist - target) * 0.02;
      const fx = (dx / dist) * pull;
      const fy = (dy / dist) * pull;
      forces[edge.a].fx += fx;
      forces[edge.a].fy += fy;
      forces[edge.b].fx -= fx;
      forces[edge.b].fy -= fy;
    }
    for (let i = 0; i < nodes.length; i++) {
      nodes[i].x += Math.max(-6, Math.min(6, forces[i].fx));
      nodes[i].y += Math.max(-6, Math.min(6, forces[i].fy));
      nodes[i].x = Math.min(WIDTH - 40, Math.max(40, nodes[i].x));
      nodes[i].y = Math.min(HEIGHT - 40, Math.max(40, nodes[i].y));
    }
  }

  return {nodes, edges};
};

export const GRAPH_WIDTH = WIDTH;
export const GRAPH_HEIGHT = HEIGHT;
