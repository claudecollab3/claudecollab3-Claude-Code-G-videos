import React from 'react';
import {StatementScene} from './StatementScene';
import {COLORS} from '../theme';

export const DemandScene: React.FC<{voDurationInFrames: number}> = ({voDurationInFrames}) => {
  return (
    <StatementScene
      eyebrow="Why It Exists"
      text="The demand comes from researchers who need publications to keep their careers — no papers, no career."
      durationInFrames={voDurationInFrames}
      keywords={[{words: ['no', 'papers', 'career'], color: COLORS.red}]}
    />
  );
};
