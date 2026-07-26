import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Background} from '../components/Background';
import {generateCitationGraph, GRAPH_WIDTH, GRAPH_HEIGHT} from '../components/citationGraph';
import {bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const NODE_COUNT = 110;

export const CitationNetworkScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const {nodes, edges} = useMemo(
    () => generateCitationGraph(NODE_COUNT, durationInFrames * 0.75),
    [durationInFrames],
  );

  // One long, unbroken camera move: starts zoomed into a dense cluster,
  // slowly pulls back and drifts across the graph to reveal the whole
  // network by the end of the scene.
  const camT = frame / durationInFrames;
  const waypoints: [number, number][] = [
    [GRAPH_WIDTH * 0.32, GRAPH_HEIGHT * 0.38],
    [GRAPH_WIDTH * 0.55, GRAPH_HEIGHT * 0.5],
    [GRAPH_WIDTH * 0.48, GRAPH_HEIGHT * 0.62],
    [GRAPH_WIDTH * 0.5, GRAPH_HEIGHT * 0.48],
  ];
  const seg = Math.min(waypoints.length - 2, Math.floor(camT * (waypoints.length - 1)));
  const segT = camT * (waypoints.length - 1) - seg;
  const eased = segT * segT * (3 - 2 * segT);
  const cx = interpolate(eased, [0, 1], [waypoints[seg][0], waypoints[seg + 1][0]]);
  const cy = interpolate(eased, [0, 1], [waypoints[seg][1], waypoints[seg + 1][1]]);
  const scale = interpolate(camT, [0, 0.55, 1], [0.42, 0.62, 0.95], {
    easing: (x) => x * x * (3 - 2 * x),
  });
  const viewW = GRAPH_WIDTH * scale;
  const viewH = viewW * (1080 / 1920);
  const vx = cx - viewW / 2;
  const vy = cy - viewH / 2;

  let flaggedVisible = 0;
  let tealVisible = 0;
  for (const n of nodes) {
    if (frame >= n.birthFrame) {
      if (n.flagged) flaggedVisible++;
      else tealVisible++;
    }
  }

  return (
    <Background>
      <svg
        viewBox={`${vx} ${vy} ${viewW} ${viewH}`}
        width="100%"
        height="100%"
        style={{position: 'absolute', inset: 0}}
      >
        {edges.map((e, i) => {
          const na = nodes[e.a];
          const nb = nodes[e.b];
          const opacity = interpolate(frame, [e.birthFrame, e.birthFrame + 20], [0, 0.28], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const flaggedEdge = na.flagged && nb.flagged;
          return (
            <line
              key={i}
              x1={na.x}
              y1={na.y}
              x2={nb.x}
              y2={nb.y}
              stroke={flaggedEdge ? COLORS.red : COLORS.teal}
              strokeWidth={flaggedEdge ? 2 : 1.2}
              opacity={opacity}
            />
          );
        })}
        {nodes.map((n) => {
          const growth = interpolate(frame, [n.birthFrame, n.birthFrame + 16], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          if (growth <= 0) return null;
          return (
            <circle
              key={n.id}
              cx={n.x}
              cy={n.y}
              r={n.radius * growth}
              fill={n.flagged ? COLORS.red : COLORS.teal}
              opacity={n.flagged ? 0.9 : 0.55}
              style={n.flagged ? {filter: `drop-shadow(0 0 5px ${COLORS.red})`} : undefined}
            />
          );
        })}
      </svg>

      <div style={{position: 'absolute', top: 90, left: 140, display: 'flex', flexDirection: 'column', gap: 6}}>
        <div
          style={{
            fontFamily: bodyFontFamily,
            fontSize: 26,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: COLORS.textDim,
          }}
        >
          Citations Build On Citations
        </div>
        <div style={{display: 'flex', gap: 32, marginTop: 8}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
            <div style={{width: 14, height: 14, borderRadius: 7, background: COLORS.red}} />
            <span style={{fontFamily: bodyFontFamily, color: COLORS.text, fontSize: 24}}>
              {flaggedVisible} flagged
            </span>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
            <div style={{width: 14, height: 14, borderRadius: 7, background: COLORS.teal}} />
            <span style={{fontFamily: bodyFontFamily, color: COLORS.text, fontSize: 24}}>
              {tealVisible} legitimate
            </span>
          </div>
        </div>
      </div>
    </Background>
  );
};
