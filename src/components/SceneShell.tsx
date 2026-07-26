import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS } from "../constants/theme";

type Props = {
  children?: React.ReactNode;
  background?: string;
};

/** Common full-bleed background wrapper every scene renders into. */
export const SceneShell: React.FC<Props> = ({ children, background = COLORS.bg }) => (
  <AbsoluteFill style={{ background }}>{children}</AbsoluteFill>
);
