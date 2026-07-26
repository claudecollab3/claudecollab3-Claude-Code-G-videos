import React from 'react';
import {AbsoluteFill} from 'remotion';
import {COLORS} from '../theme';

export const Background: React.FC<{children?: React.ReactNode}> = ({children}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bg,
        backgroundImage: `radial-gradient(ellipse at 50% 30%, ${COLORS.grid}55 0%, ${COLORS.bg} 70%)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
