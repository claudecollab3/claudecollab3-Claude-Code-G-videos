import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { PaperColumn } from "../components/PaperColumn";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";
import { jitterFor } from "../utils/seededRandom";

const FLARE_INDEX = 45;

/**
 * SC-02 (0:03-0:05): 0.4s true black hold, then the column freezes,
 * desaturates, one sheet flares red, and the camera snap-zooms onto it.
 */
export const SC02: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const blackHoldFrames = Math.round(0.4 * fps);

  if (frame < blackHoldFrames) {
    return <SceneShell background="#000000" />;
  }

  const j = jitterFor(FLARE_INDEX);
  const centerX = width / 2;
  const flareX = centerX + (j.x - 0.5) * width * 0.18;
  const flareY = height - FLARE_INDEX * 34;

  const localFrame = frame - blackHoldFrames;
  const zoomProgress = interpolate(localFrame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const scale = interpolate(zoomProgress, [0, 1], [1, 2.6]);

  const originXPct = (flareX / width) * 100;
  const originYPct = (flareY / height) * 100;

  return (
    <SceneShell>
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          transformOrigin: `${originXPct}% ${originYPct}%`,
        }}
      >
        <PaperColumn
          count={60}
          scrollY={0}
          width={width}
          height={height}
          monochrome
          flareIndex={localFrame > 3 ? FLARE_INDEX : undefined}
        />
      </AbsoluteFill>
    </SceneShell>
  );
};
