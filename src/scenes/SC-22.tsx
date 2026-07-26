import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS, FONTS } from "../constants/theme";
import { buildCitationGraph } from "../utils/citationGraph";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-22 (3:30-3:44): every flagged node gets an amber question mark; none
 * resolve back to teal. Amber takes over the frame. The legal/accuracy
 * safeguard beat — never cut for time.
 */
export const SC22: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale } = useSceneLayout(aspect);
  const durationInFrames = 14 * fps;

  const graph = useMemo(() => buildCitationGraph(width * 0.7, height * 0.7), [width, height]);
  const flaggedNodes = graph.nodes.filter((n) => n.flagged);

  const amberTakeover = interpolate(frame, [6 * fps, durationInFrames], [0, 0.9], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const captionOpacity = interpolate(frame, [3 * fps, 4 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <svg width={width * 0.7} height={height * 0.7} style={{ overflow: "visible" }}>
          {graph.links.map((link, i) => {
            const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));
            const s = nodeById.get(typeof link.source === "string" ? link.source : (link.source as unknown as { id: string }).id);
            const t = nodeById.get(typeof link.target === "string" ? link.target : (link.target as unknown as { id: string }).id);
            if (!s || !t) return null;
            return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#2C3448" strokeWidth={0.8} opacity={0.3} />;
          })}
          {graph.nodes.map((n) => (
            <circle key={n.id} cx={n.x} cy={n.y} r={n.flagged ? 9 : 5} fill={n.flagged ? COLORS.uncertain : COLORS.legit} />
          ))}
          {flaggedNodes.map((n, i) => {
            const nodeStart = (i / flaggedNodes.length) * 2 * fps;
            const scale = interpolate(frame, [nodeStart, nodeStart + 10], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <text
                key={n.id}
                x={n.x}
                y={n.y - 18}
                fill={COLORS.uncertain}
                fontFamily="Georgia, serif"
                fontWeight={700}
                fontSize={22 * scale}
                textAnchor="middle"
              >
                ?
              </text>
            );
          })}
        </svg>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background: COLORS.uncertain,
          opacity: amberTakeover,
          mixBlendMode: "multiply",
        }}
      />

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 90, opacity: captionOpacity }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 800, fontSize: 34 * fontScale, color: COLORS.text, letterSpacing: "0.02em" }}>
          FLAGGED ≠ FAKE
        </div>
        <div style={{ fontFamily: FONTS.body, fontWeight: 600, fontSize: 20 * fontScale, color: COLORS.text, opacity: 0.75, marginTop: 6 }}>
          EVERY ONE STILL NEEDS A HUMAN EXPERT
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
