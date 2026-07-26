import React from 'react';
import {StatementScene} from './StatementScene';
import {COLORS} from '../theme';

export const CalloutScene: React.FC<{voDurationInFrames: number}> = ({voDurationInFrames}) => {
  return (
    <StatementScene
      eyebrow="The Caveat"
      text="And none of it is proven fake. Flagging is a screen, not a verdict — every paper still needs a human expert."
      durationInFrames={voDurationInFrames}
      keywords={[
        {words: ['screen', 'verdict', 'fake'], color: COLORS.amber},
        {words: ['human', 'expert'], color: COLORS.teal},
      ]}
    />
  );
};
