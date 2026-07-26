import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/** SC-23 (3:44-3:55): split detect (millions/day) vs verify (one at a time), pulling back until the human is a few pixels tall. */
export const SC23: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height, fontScale, isVertical } = useSceneLayout(aspect);
  const durationInFrames = 11 * fps;

  const pullBack = interpolate(frame, [10, durationInFrames], [1, 0.12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const halfW = isVertical ? width : width / 2;
  const halfH = isVertical ? height / 2 : height;

  return (
    <SceneShell>
      <AbsoluteFill
        style={{
          transform: `scale(${pullBack})`,
          transformOrigin: "50% 50%",
          flexDirection: isVertical ? "column" : "row",
          display: "flex",
        }}
      >
        <div style={{ position: "relative", width: halfW, height: halfH, overflow: "hidden", borderRight: isVertical ? "none" : "1px solid #232B40", borderBottom: isVertical ? "1px solid #232B40" : "none" }}>
          <PaperColumn count={90} scrollY={(frame * 3) % (34 * 90)} width={halfW} height={halfH} spread={0.16} />
          <div style={{ position: "absolute", bottom: 30, left: 0, right: 0, textAlign: "center", fontFamily: FONTS.body, fontWeight: 800, fontSize: 26 * fontScale, color: COLORS.legit }}>
            DETECT: MILLIONS / DAY
          </div>
        </div>
        <div style={{ position: "relative", width: halfW, height: halfH }}>
          <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: "50%", background: COLORS.text }} />
              <div style={{ width: 50, height: 60, background: COLORS.text, borderRadius: "6px 6px 0 0" }} />
              <div style={{ width: 30, height: 18, background: COLORS.uncertain, marginTop: -20 }} />
            </div>
          </AbsoluteFill>
          <div style={{ position: "absolute", bottom: 30, left: 0, right: 0, textAlign: "center", fontFamily: FONTS.body, fontWeight: 800, fontSize: 26 * fontScale, color: COLORS.uncertain }}>
            VERIFY: 1 AT A TIME
          </div>
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
