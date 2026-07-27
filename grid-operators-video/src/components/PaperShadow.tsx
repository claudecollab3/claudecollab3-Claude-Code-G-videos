import React from 'react';
import {COLORS} from '../theme';

export type PaperShadowProps = {
  dx?: number;
  dy?: number;
  blur?: number;
  opacity?: number;
  color?: string;
  style?: React.CSSProperties;
  className?: string;
  children: React.ReactNode;
};

/**
 * CSS drop-shadow wrapper for grouping several PaperShape pieces (or any DOM
 * content) under one consistent physical shadow, lit from top-left, instead
 * of each piece casting its own and stacking oddly. Prefer PaperShape's
 * built-in feDropShadow for a single cutout; reach for this when several
 * pieces should read as one physical object.
 */
export const PaperShadow: React.FC<PaperShadowProps> = ({
  dx = 7,
  dy = 12,
  blur = 10,
  opacity = 0.3,
  color = COLORS.charcoal,
  style,
  className,
  children,
}) => {
  const rgba = hexToRgba(color, opacity);
  return (
    <div
      className={className}
      style={{
        ...style,
        filter: `drop-shadow(${dx}px ${dy}px ${blur}px ${rgba})`,
      }}
    >
      {children}
    </div>
  );
};

const hexToRgba = (hex: string, alpha: number) => {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
