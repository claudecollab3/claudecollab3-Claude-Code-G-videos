import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";
import { useSceneLayout } from "../utils/layout";

const PAPER_COUNT = 6;
const BELT_Y_FRACTION = 0.56;
const STAMP_X_FRACTION = 0.5;

/**
 * SC-07 (0:40-0:52): side-profile conveyor belt, blank documents get
 * stamped with nameplates as they pass a fixed stamp; finale shows one
 * paper with four stacked nameplates.
 */
export const SC07: React.FC<SceneProps> = ({ aspect }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { width, height } = useSceneLayout(aspect);
  const beltDurationFrames = 8 * fps;
  const beltY = height * BELT_Y_FRACTION;
  const stampX = width * STAMP_X_FRACTION;

  const stampActive = (frame % 30 < 6) && frame < beltDurationFrames;
  const stampY = stampActive ? interpolate(frame % 30, [0, 3, 6], [0, 22, 0]) : 0;

  const finaleStart = beltDurationFrames + 20;
  const finaleProgress = interpolate(frame, [finaleStart, finaleStart + 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <SceneShell>
      {frame < beltDurationFrames + 20 && (
        <AbsoluteFill>
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: beltY + 60,
              height: 10,
              background: "#2C3448",
            }}
          />
          {Array.from({ length: PAPER_COUNT }).map((_, i) => {
            const speed = width / (2.6 * fps);
            const x = ((frame + i * 55) * speed) % (width + 200) - 100;
            const passedStamp = x > stampX - 20;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: x,
                  top: beltY,
                  width: 70,
                  height: 90,
                  background: COLORS.text,
                  borderRadius: 3,
                }}
              >
                {passedStamp && (
                  <div
                    style={{
                      position: "absolute",
                      left: 8,
                      top: 12,
                      width: 54,
                      height: 12,
                      background: COLORS.uncertain,
                      borderRadius: 2,
                    }}
                  />
                )}
              </div>
            );
          })}
          <div
            style={{
              position: "absolute",
              left: stampX - 20,
              top: beltY - 70 + stampY,
              width: 40,
              height: 60,
              background: "#5B6478",
              borderRadius: 4,
            }}
          />
        </AbsoluteFill>
      )}

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          opacity: finaleProgress,
        }}
      >
        <div
          style={{
            width: 160,
            height: 210,
            background: COLORS.text,
            borderRadius: 6,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
          }}
        >
          {[0, 1, 2, 3].map((i) => {
            const barIn = interpolate(finaleProgress, [i / 4, i / 4 + 0.2], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            return (
              <div
                key={i}
                style={{
                  width: 120 * barIn,
                  height: 16,
                  background: COLORS.uncertain,
                  borderRadius: 2,
                }}
              />
            );
          })}
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};
