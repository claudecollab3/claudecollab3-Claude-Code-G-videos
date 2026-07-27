import React, {useId} from 'react';
import {COLORS} from '../theme';

export type PaperShadowSpec = {
  dx?: number;
  dy?: number;
  blur?: number;
  opacity?: number;
  color?: string;
};

export type PaperShapeProps = {
  seed: number;
  width: number;
  height: number;
  viewBox?: string;
  style?: React.CSSProperties;
  className?: string;
  /** Displacement scale for the torn-edge wobble — bigger = more ragged. */
  tornStrength?: number;
  /** Turbulence base frequency for the torn edge — smaller = broader wobbles. */
  tornFrequency?: number;
  /** Fill-texture grain strength, 0-1. */
  grainOpacity?: number;
  shadow?: PaperShadowSpec | false;
  children: React.ReactNode;
};

const DEFAULT_SHADOW: Required<PaperShadowSpec> = {
  dx: 7,
  dy: 11,
  blur: 9,
  opacity: 0.32,
  color: COLORS.charcoal,
};

/**
 * Wraps arbitrary SVG shape content (paths, polygons...) with a filter that
 * gives it: (1) hand-torn edges via feTurbulence + feDisplacementMap, seeded
 * so no two cutouts wobble identically, (2) a subtle mottled paper-grain
 * fill via a second turbulence layer multiplied over the shape, and (3) a
 * soft physical drop shadow. Every "cutout" in the video should be built by
 * passing its raw shape as children here, rather than styling shapes ad hoc.
 */
export const PaperShape: React.FC<PaperShapeProps> = ({
  seed,
  width,
  height,
  viewBox,
  style,
  className,
  tornStrength = 32,
  tornFrequency = 0.02,
  grainOpacity = 0.22,
  shadow = {},
  children,
}) => {
  const reactId = useId().replace(/[:]/g, '');
  const filterId = `paper-torn-${reactId}-${seed}`;
  const resolvedShadow = shadow === false ? null : {...DEFAULT_SHADOW, ...shadow};

  return (
    <svg
      width={width}
      height={height}
      viewBox={viewBox ?? `0 0 ${width} ${height}`}
      style={{overflow: 'visible', ...style}}
      className={className}
    >
      <defs>
        <filter id={filterId} x="-60%" y="-60%" width="220%" height="220%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency={tornFrequency}
            numOctaves={3}
            seed={seed}
            result="edgeNoise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="edgeNoise"
            scale={tornStrength}
            xChannelSelector="R"
            yChannelSelector="G"
            result="torn"
          />
          <feTurbulence
            type="fractalNoise"
            baseFrequency={0.9}
            numOctaves={2}
            seed={seed + 101}
            result="grain"
          />
          <feColorMatrix
            in="grain"
            type="matrix"
            values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.33 0.33 0.33 0 0"
            result="grainAlpha"
          />
          <feComponentTransfer in="grainAlpha" result="grainSoft">
            <feFuncA type="linear" slope={grainOpacity} intercept={0} />
          </feComponentTransfer>
          <feBlend in="torn" in2="grainSoft" mode="multiply" result="textureRaw" />
          {/* feBlend unions the two inputs' alpha, which would leak the
              full-field grain noise outside the shape as a faint halo —
              clip back to the torn shape's own alpha to prevent that. */}
          <feComposite in="textureRaw" in2="torn" operator="in" result="textured" />
          {resolvedShadow && (
            <feDropShadow
              in="textured"
              dx={resolvedShadow.dx}
              dy={resolvedShadow.dy}
              stdDeviation={resolvedShadow.blur}
              floodColor={resolvedShadow.color}
              floodOpacity={resolvedShadow.opacity}
            />
          )}
        </filter>
      </defs>
      <g filter={`url(#${filterId})`}>{children}</g>
    </svg>
  );
};
