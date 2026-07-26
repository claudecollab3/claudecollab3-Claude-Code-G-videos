import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from "d3-force";
import { seededRandom } from "./seededRandom";

export type GraphNode = { id: string; flagged: boolean; x: number; y: number };
export type GraphLink = { source: string; target: string };

const LEGIT_COUNT = 34;
const FLAGGED_COUNT = 13;

/**
 * Builds a fixed citation-network layout: flagged nodes actively cite
 * (link to) multiple legit nodes, sparser legit-legit links elsewhere. Runs
 * the force simulation synchronously to a settled layout so rendering is
 * deterministic across frames (no live simulation ticking during render).
 */
export const buildCitationGraph = (width: number, height: number) => {
  const rand = seededRandom(42);
  const nodes: GraphNode[] = [];
  for (let i = 0; i < LEGIT_COUNT; i++) {
    nodes.push({ id: `legit-${i}`, flagged: false, x: width / 2 + (rand() - 0.5) * 200, y: height / 2 + (rand() - 0.5) * 200 });
  }
  for (let i = 0; i < FLAGGED_COUNT; i++) {
    nodes.push({ id: `flag-${i}`, flagged: true, x: width / 2 + (rand() - 0.5) * 200, y: height / 2 + (rand() - 0.5) * 200 });
  }

  const links: GraphLink[] = [];
  const legitIds = nodes.filter((n) => !n.flagged).map((n) => n.id);
  const flaggedIds = nodes.filter((n) => n.flagged).map((n) => n.id);

  // Each flagged node links to several legit nodes (the "cites more" beat).
  flaggedIds.forEach((fid) => {
    const linkCount = 3 + Math.floor(rand() * 3);
    for (let i = 0; i < linkCount; i++) {
      const target = legitIds[Math.floor(rand() * legitIds.length)];
      links.push({ source: fid, target });
    }
  });
  // Sparse legit-legit links.
  for (let i = 0; i < legitIds.length; i++) {
    if (rand() < 0.3) {
      const target = legitIds[Math.floor(rand() * legitIds.length)];
      if (target !== legitIds[i]) links.push({ source: legitIds[i], target });
    }
  }

  const simulation = forceSimulation(nodes as never[])
    .force(
      "link",
      forceLink(links as never[])
        .id((d) => (d as unknown as GraphNode).id)
        .distance(70),
    )
    .force("charge", forceManyBody().strength(-55))
    .force("center", forceCenter(width / 2, height / 2))
    .force("collide", forceCollide(14))
    .stop();

  for (let i = 0; i < 300; i++) simulation.tick();

  return { nodes, links };
};
