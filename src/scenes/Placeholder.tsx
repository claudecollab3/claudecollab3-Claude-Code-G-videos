import React from "react";
import { AbsoluteFill } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS, FONTS } from "../constants/theme";
import { SceneProps } from "../types";

/** Temporary stand-in for scenes not yet built, so the timeline always renders. */
export const Placeholder: React.FC<SceneProps & { id: string }> = ({ id }) => (
  <SceneShell background="#14192B">
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: FONTS.body, fontSize: 40, color: COLORS.uncertain, opacity: 0.5 }}>
        {id}
      </div>
    </AbsoluteFill>
  </SceneShell>
);
