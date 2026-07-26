import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const IvoryTower: React.FC<{ opacity: number }> = ({ opacity }) => (
  <svg viewBox="0 0 300 400" width={300} height={400} style={{ opacity, position: "absolute" }}>
    <polygon points="150,20 190,90 110,90" fill={COLORS.text} />
    <rect x="120" y="90" width="60" height="270" fill={COLORS.text} />
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <rect key={i} x="130" y={110 + i * 40} width="16" height="24" fill="#0A0E1A" />
    ))}
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <rect key={`b${i}`} x="154" y={110 + i * 40} width="16" height="24" fill="#0A0E1A" />
    ))}
  </svg>
);

const Factory: React.FC<{ opacity: number; smokeFrame: number }> = ({ opacity, smokeFrame }) => (
  <svg viewBox="0 0 300 400" width={300} height={400} style={{ opacity, position: "absolute" }}>
    <rect x="60" y="220" width="200" height="140" fill={COLORS.text} />
    <rect x="90" y="140" width="30" height="90" fill={COLORS.text} />
    <rect x="150" y="110" width="30" height="120" fill={COLORS.text} />
    <rect x="210" y="150" width="30" height="80" fill={COLORS.text} />
    {[0, 1, 2].map((stack) => {
      const stackX = [105, 165, 225][stack];
      const baseY = [140, 110, 150][stack];
      return [0, 1, 2].map((puff) => {
        const t = (smokeFrame + puff * 12 + stack * 6) % 48;
        const rise = interpolate(t, [0, 48], [0, 90]);
        const puffOpacity = interpolate(t, [0, 10, 40, 48], [0, 0.5, 0.2, 0]);
        return (
          <circle
            key={`${stack}-${puff}`}
            cx={stackX + 15}
            cy={baseY - rise}
            r={10 + rise * 0.15}
            fill={COLORS.uncertain}
            opacity={puffOpacity}
          />
        );
      });
    })}
  </svg>
);

const IconRow: React.FC<{ opacity: number; scale: number }> = ({ opacity, scale }) => (
  <div
    style={{
      display: "flex",
      gap: 60,
      opacity,
      transform: `scale(${scale})`,
    }}
  >
    {["Invoice", "Clock", "Cart"].map((label) => (
      <div key={label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 12,
            border: `3px solid ${COLORS.uncertain}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {label === "Invoice" && (
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
              <rect x="4" y="2" width="16" height="20" rx="1" stroke={COLORS.uncertain} strokeWidth="2" />
              <line x1="7" y1="8" x2="17" y2="8" stroke={COLORS.uncertain} strokeWidth="2" />
              <line x1="7" y1="13" x2="17" y2="13" stroke={COLORS.uncertain} strokeWidth="2" />
              <line x1="7" y1="18" x2="13" y2="18" stroke={COLORS.uncertain} strokeWidth="2" />
            </svg>
          )}
          {label === "Clock" && (
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke={COLORS.uncertain} strokeWidth="2" />
              <line x1="12" y1="12" x2="12" y2="7" stroke={COLORS.uncertain} strokeWidth="2" />
              <line x1="12" y1="12" x2="16" y2="14" stroke={COLORS.uncertain} strokeWidth="2" />
            </svg>
          )}
          {label === "Cart" && (
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
              <path d="M3 4h2l2.4 12.4a2 2 0 002 1.6h7.2a2 2 0 002-1.6L20 8H6" stroke={COLORS.uncertain} strokeWidth="2" fill="none" />
              <circle cx="10" cy="20" r="1.4" fill={COLORS.uncertain} />
              <circle cx="17" cy="20" r="1.4" fill={COLORS.uncertain} />
            </svg>
          )}
        </div>
      </div>
    ))}
  </div>
);

/** SC-06 (0:30-0:40): ivory-tower silhouette crossfades into a factory. */
export const SC06: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fontScale } = useSceneLayout(aspect);

  const morphProgress = interpolate(frame, [30, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const iconsOpacity = interpolate(frame, [110, 130], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 40 }}>
        <div style={{ position: "relative", width: 300, height: 400 }}>
          <IvoryTower opacity={1 - morphProgress} />
          <Factory opacity={morphProgress} smokeFrame={frame} />
        </div>
        <div style={{ transform: `scale(${fontScale})` }}>
          <IconRow opacity={iconsOpacity} scale={interpolate(iconsOpacity, [0, 1], [0.85, 1])} />
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
