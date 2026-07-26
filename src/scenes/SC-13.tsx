import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";
import { buildWhorlRidges } from "../utils/whorl";

const RIDGE_COUNT = 26;
const BAR_COUNT = 6;

/**
 * SC-13 (1:42-1:54) — hero shot. The SC-05 highlight bars overlay and
 * resolve into a procedurally generated fingerprint whorl, built from
 * stacked thin ridge strokes drawn on progressively. Pushes in to center.
 */
export const SC13: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const durationInFrames = 12 * fps;

  const centerX = width / 2;
  const centerY = height / 2;
  const maxRadius = Math.min(width, height) * 0.34;
  const minRadius = maxRadius * 0.12;
  const radiusStep = (maxRadius - minRadius) / RIDGE_COUNT;

  const ridges = useMemo(
    () => buildWhorlRidges(centerX, centerY, RIDGE_COUNT, minRadius, radiusStep),
    [centerX, centerY, minRadius, radiusStep],
  );

  // Highlight bars (from SC-05) fade out as the whorl resolves in.
  const barsOpacity = interpolate(frame, [0, 40], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const whorlDrawStart = 14;

  const pushInStart = durationInFrames - 4 * fps;
  const pushInScale = interpolate(frame, [pushInStart, durationInFrames], [1, 1.9], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", gap: 10, opacity: barsOpacity }}>
        {Array.from({ length: BAR_COUNT }).map((_, i) => (
          <div key={i} style={{ width: 260 - i * 12, height: 7, background: COLORS.legit, borderRadius: 3 }} />
        ))}
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          transform: `scale(${pushInScale})`,
          transformOrigin: `${(centerX / width) * 100}% ${(centerY / height) * 100}%`,
        }}
      >
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: "absolute", inset: 0 }}>
          {ridges.map((ridge, i) => {
            const ridgeStart = whorlDrawStart + i * 1.3;
            const drawProgress = interpolate(frame, [ridgeStart, ridgeStart + 26], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            const dashOffset = ridge.approxLength * (1 - drawProgress);
            return (
              <path
                key={i}
                d={ridge.d}
                fill="none"
                stroke={COLORS.legit}
                strokeWidth={1.6}
                strokeLinecap="round"
                opacity={0.85}
                strokeDasharray={ridge.approxLength}
                strokeDashoffset={dashOffset}
              />
            );
          })}
        </svg>
      </AbsoluteFill>
    </SceneShell>
  );
};
