import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { WorldMap } from "../components/WorldMap";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-04 (0:12-0:18): desaturated world map, red dots bloom simultaneously
 * across 40+ countries, slow orthographic pan left->right. Text strikes
 * through "NOT ONE JOURNAL" / "NOT ONE COUNTRY".
 */
export const SC04: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale } = useSceneLayout(aspect);
  const durationInFrames = 6 * fps;

  const rotateLambda = interpolate(frame, [0, durationInFrames], [30, -30], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dotBloom = interpolate(frame, [8, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const strike1Progress = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const strike2Progress = interpolate(frame, [70, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const strike2Opacity = interpolate(frame, [64, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const strikeLabelStyle: React.CSSProperties = {
    fontFamily: FONTS.body,
    fontWeight: 800,
    fontSize: 40 * fontScale,
    color: COLORS.text,
    letterSpacing: "0.03em",
    position: "relative",
  };

  return (
    <SceneShell>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", filter: "saturate(0.35)" }}>
        <WorldMap width={width} height={height} rotateLambda={rotateLambda} dotBloom={dotBloom} />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: 18,
          paddingBottom: height * 0.15,
        }}
      >
        <div style={strikeLabelStyle}>
          NOT ONE JOURNAL
          <div
            style={{
              position: "absolute",
              left: 0,
              top: "50%",
              height: 4,
              background: COLORS.flagged,
              width: `${strike1Progress * 100}%`,
            }}
          />
        </div>
        <div style={{ ...strikeLabelStyle, opacity: strike2Opacity }}>
          NOT ONE COUNTRY
          <div
            style={{
              position: "absolute",
              left: 0,
              top: "50%",
              height: 4,
              background: COLORS.flagged,
              width: `${strike2Progress * 100}%`,
            }}
          />
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
