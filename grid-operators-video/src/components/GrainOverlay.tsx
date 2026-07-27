import React from 'react';

/**
 * Full-frame paper grain: a static SVG turbulence field multiplied over
 * everything at low opacity, so the whole tabletop reads as textured paper
 * rather than a flat digital background.
 */
export const GrainOverlay: React.FC<{opacity?: number}> = ({opacity = 0.05}) => {
  return (
    <svg
      width="100%"
      height="100%"
      style={{
        position: 'absolute',
        inset: 0,
        mixBlendMode: 'multiply',
        opacity,
        pointerEvents: 'none',
      }}
    >
      <filter id="global-grain">
        <feTurbulence type="fractalNoise" baseFrequency={0.85} numOctaves={2} seed={11} stitchTiles="stitch" />
        <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0.3 0.2 0 0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#global-grain)" />
    </svg>
  );
};
