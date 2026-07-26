import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

/**
 * SC-24 (3:55-4:00) — final frame. "WHO CHECKS THEM?" holds over a paper
 * column that keeps scrolling upward at constant velocity — it never
 * resolves, so whichever frame the video ends on lands mid-scroll.
 */
export const SC24: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { width, height, fontScale } = useSceneLayout(aspect);

  return (
    <SceneShell>
      <AbsoluteFill style={{ opacity: 0.6 }}>
        <PaperColumn count={140} scrollY={frame * 4} width={width} height={height} spread={0.1} />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          background: "linear-gradient(180deg, rgba(10,14,26,0.2) 0%, rgba(10,14,26,0.85) 60%, rgba(10,14,26,0.95) 100%)",
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 800,
            fontSize: 56 * fontScale,
            color: COLORS.text,
            letterSpacing: "0.02em",
            textAlign: "center",
          }}
        >
          WHO CHECKS THEM?
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
