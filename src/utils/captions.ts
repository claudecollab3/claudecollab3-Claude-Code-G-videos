import { MAIN_ACTS } from "../constants/script";
import { resolveTimeline } from "./timeline";
import { CaptionWord } from "../components/CaptionCard";

export type CaptionCardData = {
  startFrame: number;
  durationInFrames: number;
  words: CaptionWord[];
};

const WORDS_PER_CARD = 4;

/**
 * Builds burned-in caption cards for the whole MainVideo timeline. Without
 * real VO audio to force-align against (see scripts/generate-vo.ts's
 * placeholder-silence fallback), word timing is estimated by distributing
 * each act's real rendered duration across its words, weighted by word
 * length. Re-run once real narration + whisper-timestamped alignment are
 * available to replace this estimate with frame-accurate timing.
 */
export const buildCaptionCards = (fps: number): CaptionCardData[] => {
  const { acts } = resolveTimeline(fps);
  const actById = new Map(acts.map((a) => [a.id, a]));
  const cards: CaptionCardData[] = [];

  for (const act of MAIN_ACTS) {
    const resolved = actById.get(act.id);
    if (!resolved) continue;
    const words = act.text.split(/\s+/).filter(Boolean);
    const weights = words.map((w) => Math.max(2, w.replace(/[^a-zA-Z0-9]/g, "").length));
    const totalWeight = weights.reduce((s, w) => s + w, 0);

    let cursorFrame = resolved.startFrame;
    const wordFrames: { text: string; startFrame: number }[] = [];
    for (let i = 0; i < words.length; i++) {
      const wordDuration = (weights[i] / totalWeight) * resolved.durationInFrames;
      wordFrames.push({ text: words[i], startFrame: Math.round(cursorFrame) });
      cursorFrame += wordDuration;
    }

    for (let i = 0; i < wordFrames.length; i += WORDS_PER_CARD) {
      const chunk = wordFrames.slice(i, i + WORDS_PER_CARD);
      const cardStart = chunk[0].startFrame;
      const nextChunkStart = wordFrames[i + WORDS_PER_CARD]?.startFrame;
      const cardEnd = nextChunkStart ?? resolved.startFrame + resolved.durationInFrames;
      cards.push({
        startFrame: cardStart,
        durationInFrames: Math.max(6, cardEnd - cardStart),
        words: chunk.map((w) => ({ text: w.text, startFrame: w.startFrame - cardStart })),
      });
    }
  }

  return cards;
};
