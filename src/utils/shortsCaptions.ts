import shortsTimings from "../../public/audio/shorts/timings.json";
import { SHORTS_ACTS } from "../constants/shortsScript";
import { CaptionCardData } from "./captions";

const WORDS_PER_CARD = 4;

/** Same word-timing-estimate approach as buildCaptionCards, against the shorts VO manifest. */
export const buildShortsCaptionCards = (fps: number): CaptionCardData[] => {
  const actById = new Map(shortsTimings.acts.map((a) => [a.id, a]));
  const cards: CaptionCardData[] = [];

  for (const act of SHORTS_ACTS) {
    const resolved = actById.get(act.id);
    if (!resolved) continue;
    const startFrame = Math.round(resolved.startSeconds * fps);
    const durationInFrames = Math.round(resolved.durationSeconds * fps);
    const words = act.text.split(/\s+/).filter(Boolean);
    const weights = words.map((w) => Math.max(2, w.replace(/[^a-zA-Z0-9]/g, "").length));
    const totalWeight = weights.reduce((s, w) => s + w, 0);

    let cursorFrame = startFrame;
    const wordFrames: { text: string; startFrame: number }[] = [];
    for (let i = 0; i < words.length; i++) {
      const wordDuration = (weights[i] / totalWeight) * durationInFrames;
      wordFrames.push({ text: words[i], startFrame: Math.round(cursorFrame) });
      cursorFrame += wordDuration;
    }

    for (let i = 0; i < wordFrames.length; i += WORDS_PER_CARD) {
      const chunk = wordFrames.slice(i, i + WORDS_PER_CARD);
      const cardStart = chunk[0].startFrame;
      const nextChunkStart = wordFrames[i + WORDS_PER_CARD]?.startFrame;
      const cardEnd = nextChunkStart ?? startFrame + durationInFrames;
      cards.push({
        startFrame: cardStart,
        durationInFrames: Math.max(6, cardEnd - cardStart),
        words: chunk.map((w) => ({ text: w.text, startFrame: w.startFrame - cardStart })),
      });
    }
  }

  return cards;
};
