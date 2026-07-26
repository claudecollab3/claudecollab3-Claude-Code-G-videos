import React from 'react';
import {StatementScene} from './StatementScene';
import {COLORS} from '../theme';

export const PaperMillDefScene: React.FC<{voDurationInFrames: number}> = ({voDurationInFrames}) => {
  return (
    <StatementScene
      eyebrow="What Is A Paper Mill"
      text="A paper mill is a company that sells finished research papers with your name on it, or sells you an author slot on someone else's."
      durationInFrames={voDurationInFrames}
      keywords={[{words: ['sells', 'company'], color: COLORS.amber}]}
    />
  );
};
