import React from "react";

type Props = {
  /** Per-frame velocity, in px, used to place trailing ghost copies. */
  dx?: number;
  dy?: number;
  steps?: number;
  opacityFalloff?: number;
  children: React.ReactNode;
};

/**
 * Fakes a 180°-shutter motion-blur trail by stacking fading ghost copies of
 * `children` behind its current position, offset by per-frame velocity.
 * Used on graphic moves in place of a real blur filter (cheaper to render).
 */
export const MotionBlurGhost: React.FC<Props> = ({
  dx = 0,
  dy = 0,
  steps = 4,
  opacityFalloff = 0.45,
  children,
}) => {
  if (Math.abs(dx) < 0.05 && Math.abs(dy) < 0.05) {
    return <>{children}</>;
  }
  const ghosts = [];
  for (let i = steps; i >= 1; i--) {
    const opacity = Math.pow(opacityFalloff, i);
    ghosts.push(
      <div
        key={i}
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${-dx * i * 0.5}px, ${-dy * i * 0.5}px)`,
          opacity,
        }}
      >
        {children}
      </div>,
    );
  }
  return (
    <div style={{ position: "relative" }}>
      {ghosts}
      <div style={{ position: "relative" }}>{children}</div>
    </div>
  );
};
