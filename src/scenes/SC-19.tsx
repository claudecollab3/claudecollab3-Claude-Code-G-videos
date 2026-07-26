import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, useCurrentFrame, useVideoConfig, staticFile } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { COLORS } from "../constants/theme";
import { SceneProps } from "../types";

/**
 * SC-19 (2:50-3:00) — the twist gate. Full color drain to monochrome, 0.5s
 * hold, a single red node starts pulsing under a slow dolly-back. Audio
 * drops to near-silence except a heartbeat pulse.
 *
 * TODO: the spec also calls for a continuous sub-bass drone bed (ducked
 * -12dB under VO, full drop here) across the whole video — no royalty-free
 * asset was available to source, so only this scene's heartbeat SFX is
 * wired up; the drone bed itself is not yet implemented.
 */
export const SC19: React.FC<SceneProps> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationInFrames = 10 * fps;

  const drainEnd = 0.6 * fps;
  const holdEnd = drainEnd + 0.5 * fps;
  const saturate = interpolate(frame, [0, drainEnd], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dollyScale = interpolate(frame, [holdEnd, durationInFrames], [1.15, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pulsePhase = ((frame - holdEnd) % (1 * fps)) / fps;
  const pulseActive = frame >= holdEnd;
  const pulseScale = pulseActive ? 1 + Math.max(0, 0.35 - pulsePhase * 1.2) : 0;

  const beatFrames: number[] = [];
  for (let t = holdEnd; t < durationInFrames; t += fps) {
    beatFrames.push(Math.round(t));
    beatFrames.push(Math.round(t + fps * 0.22));
  }

  return (
    <SceneShell>
      {beatFrames.map((f, i) => (
        <Sequence key={i} from={f} durationInFrames={Math.round(fps * 0.2)}>
          <Audio src={staticFile("audio/sfx/heartbeat-thump.wav")} />
        </Sequence>
      ))}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          filter: `saturate(${saturate})`,
          transform: `scale(${dollyScale})`,
        }}
      >
        <div
          style={{
            width: 26,
            height: 26,
            borderRadius: "50%",
            background: COLORS.flagged,
            transform: `scale(${pulseScale})`,
            boxShadow: `0 0 ${40 * pulseScale}px ${10 * pulseScale}px ${COLORS.flagged}`,
            opacity: pulseActive ? 1 : 0,
          }}
        />
      </AbsoluteFill>
    </SceneShell>
  );
};
