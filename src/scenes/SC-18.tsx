import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WorldMap } from "../components/WorldMap";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

// India cluster (indices in FLAGGED_COUNTRY_DOTS: 24 = Delhi, 46/47 = Mumbai/Hyderabad).
const REGION_INDICES = [24, 46, 47];

/**
 * SC-18 (2:34-2:50): return to SC-04's map. One region consolidates, holds,
 * then mandatorily zooms back out to show all other dots still present —
 * keeps this a systems story, not a nationalism story. Banknote icon.
 * Shifts to amber on the final line.
 */
export const SC18: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale } = useSceneLayout(aspect);

  const zoomInEnd = 5 * fps;
  const holdEnd = zoomInEnd + 1.5 * fps;
  const zoomOutEnd = holdEnd + 4 * fps;

  const zoomProgress = interpolate(frame, [0, zoomInEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const zoomOutProgress = interpolate(frame, [holdEnd, zoomOutEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  // 1 while consolidated, back to 0 once fully zoomed back out.
  const consolidation = zoomProgress * (1 - zoomOutProgress);

  const mapScale = interpolate(consolidation, [0, 1], [1, 2.4]);
  const dotScale = interpolate(consolidation, [0, 1], [1, 2.2]);

  const amberShift = interpolate(frame, [zoomOutEnd, zoomOutEnd + 1.5 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const labelOpacity = interpolate(frame, [zoomInEnd - 20, zoomInEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", transform: `scale(${mapScale})`, filter: "saturate(0.4)" }}>
        <WorldMap width={width} height={height} rotateLambda={-77} dotBloom={1} dotColor={amberShift > 0.5 ? COLORS.uncertain : COLORS.flagged} />
        <AbsoluteFill>
          <WorldMap
            width={width}
            height={height}
            rotateLambda={-77}
            dotBloom={consolidation}
            dotRadius={6 * dotScale}
            dotColor={amberShift > 0.5 ? COLORS.uncertain : COLORS.flagged}
            onlyIndices={REGION_INDICES}
          />
        </AbsoluteFill>
      </AbsoluteFill>

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-end", paddingBottom: 90, opacity: labelOpacity * (1 - zoomOutProgress) }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 22 * fontScale, color: COLORS.text, opacity: 0.85 }}>
          ONE COUNTRY&apos;S INSTITUTIONS: ~35% OF ITS CANCER OUTPUT
        </div>
      </AbsoluteFill>

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 90, opacity: interpolate(zoomOutProgress, [0.6, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
          <svg width="34" height="24" viewBox="0 0 34 24">
            <rect x="1" y="1" width="32" height="22" rx="3" stroke={COLORS.uncertain} strokeWidth="2" fill="none" />
            <circle cx="17" cy="12" r="6" stroke={COLORS.uncertain} strokeWidth="2" fill="none" />
          </svg>
          <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 20 * fontScale, color: COLORS.uncertain }}>
            A SYSTEM THAT PAYS FOR PUBLICATION, EVERYWHERE
          </div>
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
