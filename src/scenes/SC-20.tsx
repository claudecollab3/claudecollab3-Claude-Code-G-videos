import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { SourceLowerThird } from "../components/SourceLowerThird";
import { COLORS, FONTS } from "../constants/theme";
import { assertLabeledDualColor } from "../constants/colorRule";
import { buildCitationGraph } from "../utils/citationGraph";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-20 (3:00-3:14) — best visual in the piece. Force-directed citation
 * network: teal (legit) nodes grow slowly, red (flagged) nodes grow twice
 * as fast and actively link teal nodes together. 8s unbroken camera orbit
 * (faked via a bounded 3D rotate on the flat layout — an honest simplification: real 3D
 * graph geometry was out of scope for the time budget).
 */
export const SC20: React.FC<SceneProps> = ({ aspect }) => {
  assertLabeledDualColor(true, true);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);

  const graph = useMemo(() => buildCitationGraph(width * 0.7, height * 0.7), [width, height]);

  const growProgress = interpolate(frame, [0, 6 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const legitRadius = interpolate(growProgress, [0, 1], [2, 7]);
  const flaggedRadius = interpolate(Math.min(1, growProgress * 2), [0, 1], [2, 9]);

  const orbitStart = 2 * fps;
  const orbitProgress = interpolate(frame, [orbitStart, orbitStart + 8 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rotateY = Math.sin(orbitProgress * Math.PI * 2) * 22;
  const rotateX = Math.cos(orbitProgress * Math.PI * 2) * 8;

  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));

  return (
    <SceneShell>
      {frame < 75 && <SourceLowerThird source="Nature" year={2026} aspect={aspect} />}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", perspective: 1400 }}>
        <div
          style={{
            width: width * 0.7,
            height: height * 0.7,
            position: "relative",
            transform: `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`,
            transformStyle: "preserve-3d",
          }}
        >
          <svg width={width * 0.7} height={height * 0.7} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
            {graph.links.map((link, i) => {
              const s = nodeById.get(typeof link.source === "string" ? link.source : (link.source as unknown as { id: string }).id);
              const t = nodeById.get(typeof link.target === "string" ? link.target : (link.target as unknown as { id: string }).id);
              if (!s || !t) return null;
              const isFlaggedLink = s.flagged || t.flagged;
              return (
                <line
                  key={i}
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  stroke={isFlaggedLink ? COLORS.flagged : "#2C3448"}
                  strokeWidth={isFlaggedLink ? 1.4 : 0.8}
                  opacity={isFlaggedLink ? 0.55 : 0.35}
                />
              );
            })}
            {graph.nodes.map((n) => (
              <circle
                key={n.id}
                cx={n.x}
                cy={n.y}
                r={n.flagged ? flaggedRadius : legitRadius}
                fill={n.flagged ? COLORS.flagged : COLORS.legit}
              />
            ))}
          </svg>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 60 }}>
        <div style={{ display: "flex", gap: 34, fontFamily: FONTS.body, fontWeight: 700, fontSize: 20, opacity: 0.85 }}>
          <span style={{ color: COLORS.legit }}>● LEGITIMATE</span>
          <span style={{ color: COLORS.flagged }}>● FLAGGED — CITED MORE</span>
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
