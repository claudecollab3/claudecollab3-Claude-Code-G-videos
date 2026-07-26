/**
 * Generates the condensed 7-act ShortsCut VO track. Same mechanics as
 * generate-vo.ts — see scripts/lib/voGen.ts.
 */
import path from "node:path";
import { SHORTS_ACTS } from "../src/constants/shortsScript";
import { generateVoTrack } from "./lib/voGen";

generateVoTrack({
  acts: SHORTS_ACTS,
  outDir: path.join(__dirname, "..", "public", "audio", "shorts"),
  label: "shorts",
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
