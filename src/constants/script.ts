export type Act = {
  id: string;
  title: string;
  text: string;
  /** Estimated seconds from the storyboard markers — used only until
   * public/audio/timings.json (real ElevenLabs render durations) exists. */
  estimatedSeconds: number;
};

export const MAIN_ACTS: Act[] = [
  {
    id: "act-01",
    title: "Cold open",
    text: "Someone built an AI to read two point six million cancer studies. It came back with a number nobody wanted.",
    estimatedSeconds: 5,
  },
  {
    id: "act-02",
    title: "The number",
    text: "Two hundred and fifty thousand. Two hundred and fifty thousand cancer papers — roughly one in ten — written in a way that matches papers already retracted for being fabricated. Not one journal. Not one country. One in ten. And here's what makes it strange. Nobody found these by reading them. They found them by noticing that they all sounded the same.",
    estimatedSeconds: 25,
  },
  {
    id: "act-03",
    title: "Paper mills",
    text: "To understand why, you need to know what a paper mill is. A paper mill is a company. It has customers, pricing, and delivery times. What it sells is science. You send money. They send back a finished research paper with your name on it — or they sell you an author slot on a paper somebody else paid for. The customer is usually a doctor or a researcher in a system that requires publications for promotion. No papers, no career. The demand is real. So the supply became industrial. Estimates put it at more than four hundred thousand suspected papers in twenty years, and tens of millions of dollars a year in revenue. In two years, one publisher retracted around eleven thousand papers and shut down nineteen entire journals. Nineteen journals. Deleted. But nobody could measure the whole problem. Two point six million cancer papers is more than any team could ever read. So a group of researchers stopped trying to read them.",
    estimatedSeconds: 60,
  },
  {
    id: "act-04",
    title: "The fingerprint",
    text: "Here's the insight that cracked it. A factory that makes thousands of papers can't write each one from scratch. It uses templates. And templates leave a residue — the same sentence shapes, the same hedges, the same strange rhythms, appearing again and again across papers that share no authors, no topic, and no country. A fingerprint made of grammar. So the team trained a language model on papers already retracted as paper-mill products, and taught it to recognise that fingerprint. Then they aimed it at twenty-five years of cancer research. Accuracy in testing: about ninety-one percent. Result: nine point eight seven percent of the literature flagged. And the shape of that result is worse than the size of it. First — it's growing. The flagged share in twenty twenty-four is dramatically higher than in nineteen ninety-nine. Second — it is not confined to obscure journals. The rise shows up inside the top ten percent of journals by impact factor. The prestigious ones. Third — over a hundred and seventy thousand flagged papers came from one country's institutions. Around thirty-five percent of its cancer output in this dataset. Not because its scientists are worse. Because its promotion system made publication the currency — and where you make something a currency, someone will start printing it.",
    estimatedSeconds: 80,
  },
  {
    id: "act-05",
    title: "The twist",
    text: "Now the part that changes what this story is about. You'd assume fake research just sits there, ignored. Dead weight in a database. It doesn't. Reporting in Nature found that suspected paper-mill cancer papers were pulling in more citations than legitimate ones. Read that again. The suspect work is spreading faster than the real work. Because a fabricated result is clean. No messy data, no null findings, no contradictions. It's exactly what a busy researcher is looking for when they need a citation to support the next study. So real scientists build on it. Real trials get designed around it. Real funding gets allocated toward it. The fraud stops being a stain on the record. It becomes part of the foundation.",
    estimatedSeconds: 40,
  },
  {
    id: "act-06",
    title: "The caveat",
    text: "And notice what the researchers refuse to say. They will not call a single one of those papers fake. Flagging is a screen, not a verdict. Every one still needs a human expert to check. Which leaves us with the actual problem. We can now detect this at the scale of millions. We can only verify it one paper at a time. A machine found a quarter of a million questions in an afternoon. There is no machine that can answer them.",
    estimatedSeconds: 25,
  },
  {
    id: "act-07",
    title: "Button",
    text: "So — who checks two hundred and fifty thousand papers? And what happens to the ones nobody gets to?",
    estimatedSeconds: 5,
  },
];

export const SHORTS_SCRIPT =
  "Someone built an AI to read two point six million cancer studies. It flagged two hundred and fifty thousand of them. One in ten cancer papers — written in a way that matches papers already retracted for being fabricated. They weren't caught by reading them. They were caught because they all sounded the same. Paper mills are companies that sell finished research papers with your name on it. They use templates. Templates leave a fingerprint. So researchers trained a model to spot the fingerprint and aimed it at twenty-five years of cancer research. Nine point eight seven percent flagged. Rising. And rising inside the top ten percent of journals. Then the part that changes everything: Nature reported the suspected papers were getting more citations than the real ones. Real trials get built on top of them. The fraud isn't a stain on the record. It's the foundation. And nobody's called a single one fake yet. There's no machine that can check them.";

export const TOTAL_ESTIMATED_SECONDS = MAIN_ACTS.reduce((sum, a) => sum + a.estimatedSeconds, 0);
