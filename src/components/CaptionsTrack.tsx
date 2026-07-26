import React from "react";
import { Sequence } from "remotion";
import { CaptionCard } from "./CaptionCard";
import { CaptionCardData } from "../utils/captions";
import { Aspect } from "../types";

export const CaptionsTrack: React.FC<{ aspect: Aspect; cards: CaptionCardData[] }> = ({ aspect, cards }) => {
  return (
    <>
      {cards.map((card, i) => (
        <Sequence key={i} from={card.startFrame} durationInFrames={card.durationInFrames}>
          <CaptionCard words={card.words} aspect={aspect} />
        </Sequence>
      ))}
    </>
  );
};
