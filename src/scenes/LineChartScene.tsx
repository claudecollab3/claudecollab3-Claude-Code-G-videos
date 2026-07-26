import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {CountUp} from '../components/CountUp';
import {condensedFontFamily, bodyFontFamily} from '../fonts';
import {COLORS} from '../theme';

const CHART_LEFT = 220;
const CHART_RIGHT = 1500;
const CHART_TOP = 220;
const CHART_BOTTOM = 780;
const YEARS = 26; // 1999-2024

// Smooth ease-in growth curve, exaggerated toward the end (mirrors the
// "growing, and growing fastest" framing).
const growth = (t: number, power: number) => Math.pow(t, power);

const buildPath = (maxValue: number, power: number) => {
  const points: [number, number][] = [];
  for (let i = 0; i < YEARS; i++) {
    const t = i / (YEARS - 1);
    const value = growth(t, power) * maxValue;
    const x = CHART_LEFT + (t * (CHART_RIGHT - CHART_LEFT));
    const y = CHART_BOTTOM - (value / 14) * (CHART_BOTTOM - CHART_TOP);
    points.push([x, y]);
  }
  return points;
};

const toPath = (points: [number, number][]) =>
  points.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');

export const LineChartScene: React.FC = () => {
  const frame = useCurrentFrame();
  const overall = buildPath(9.87, 1.6);
  const topJournals = buildPath(13.5, 1.9);

  const drawProgress = interpolate(frame, [10, 260], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const visibleCount = Math.max(2, Math.round(drawProgress * YEARS));

  const overallPath = toPath(overall.slice(0, visibleCount));
  const topPath = toPath(topJournals.slice(0, visibleCount));

  const endOverall = overall[visibleCount - 1];
  const endTop = topJournals[visibleCount - 1];

  return (
    <Background>
      <svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{position: 'absolute', inset: 0}}>
        <line x1={CHART_LEFT} y1={CHART_BOTTOM} x2={CHART_RIGHT} y2={CHART_BOTTOM} stroke={COLORS.grid} strokeWidth={2} />
        <line x1={CHART_LEFT} y1={CHART_TOP} x2={CHART_LEFT} y2={CHART_BOTTOM} stroke={COLORS.grid} strokeWidth={2} />

        <path d={topPath} fill="none" stroke={COLORS.amber} strokeWidth={4} strokeLinecap="round" opacity={0.9} />
        <path d={overallPath} fill="none" stroke={COLORS.red} strokeWidth={6} strokeLinecap="round" />

        {endOverall && (
          <circle cx={endOverall[0]} cy={endOverall[1]} r={9} fill={COLORS.red} style={{filter: `drop-shadow(0 0 10px ${COLORS.red})`}} />
        )}
        {endTop && (
          <circle cx={endTop[0]} cy={endTop[1]} r={7} fill={COLORS.amber} />
        )}

        <text x={CHART_LEFT} y={CHART_BOTTOM + 46} fill={COLORS.textDim} fontSize={26} fontFamily={undefined}>
          1999
        </text>
        <text x={CHART_RIGHT - 60} y={CHART_BOTTOM + 46} fill={COLORS.textDim} fontSize={26}>
          2024
        </text>
      </svg>

      <div style={{position: 'absolute', top: 90, left: 140, display: 'flex', flexDirection: 'column', gap: 10}}>
        <div
          style={{
            fontFamily: bodyFontFamily,
            fontSize: 26,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: COLORS.textDim,
          }}
        >
          Flagged Share of the Literature
        </div>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
          <CountUp to={91} startFrame={20} durationInFrames={60} color={COLORS.teal} fontSize={104} suffix="%" />
          <span style={{fontFamily: bodyFontFamily, fontSize: 30, color: COLORS.textDim}}>model accuracy</span>
        </div>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
          <CountUp to={9.87} startFrame={80} durationInFrames={90} color={COLORS.red} fontSize={104} suffix="%" format={(n) => n.toFixed(2)} />
          <span style={{fontFamily: bodyFontFamily, fontSize: 30, color: COLORS.textDim}}>of the literature flagged</span>
        </div>
      </div>

      <div style={{position: 'absolute', bottom: 200, right: 220, display: 'flex', alignItems: 'center', gap: 12}}>
        <div style={{width: 22, height: 4, background: COLORS.amber}} />
        <div style={{fontFamily: condensedFontFamily, fontSize: 26, color: COLORS.amber}}>
          Top 10% journals by impact factor — growing fastest
        </div>
      </div>
    </Background>
  );
};
