import { Act } from "./script";

/** The condensed Shorts VO, split into the same 7-act shape as MainVideo. */
export const SHORTS_ACTS: Act[] = [
  {
    id: "act-01",
    title: "Cold open",
    text: "Someone built an AI to read two point six million cancer studies.",
    estimatedSeconds: 3,
  },
  {
    id: "act-02",
    title: "The number",
    text: "It flagged two hundred and fifty thousand of them. One in ten cancer papers — written in a way that matches papers already retracted for being fabricated.",
    estimatedSeconds: 8,
  },
  {
    id: "act-03",
    title: "Paper mills",
    text: "They weren't caught by reading them. They were caught because they all sounded the same. Paper mills are companies that sell finished research papers with your name on it.",
    estimatedSeconds: 10,
  },
  {
    id: "act-04",
    title: "The fingerprint",
    text: "They use templates. Templates leave a fingerprint. So researchers trained a model to spot the fingerprint and aimed it at twenty-five years of cancer research. Nine point eight seven percent flagged. Rising. And rising inside the top ten percent of journals.",
    estimatedSeconds: 16,
  },
  {
    id: "act-05",
    title: "The twist",
    text: "Then the part that changes everything: Nature reported the suspected papers were getting more citations than the real ones. Real trials get built on top of them. The fraud isn't a stain on the record. It's the foundation.",
    estimatedSeconds: 12,
  },
  {
    id: "act-06",
    title: "The caveat",
    text: "And nobody's called a single one fake yet.",
    estimatedSeconds: 6,
  },
  {
    id: "act-07",
    title: "Button",
    text: "There's no machine that can check them.",
    estimatedSeconds: 3,
  },
];

export const SHORTS_TOTAL_ESTIMATED_SECONDS = SHORTS_ACTS.reduce(
  (sum, a) => sum + a.estimatedSeconds,
  0,
);
