/**
 * Generates the 7-act MainVideo VO track via ElevenLabs (voice "Adam") and
 * writes public/audio/timings.json, which src/utils/timeline.ts reads to
 * derive real scene durations. See scripts/lib/voGen.ts for the
 * placeholder-silence fallback used when ELEVENLABS_API_KEY isn't set.
 */
import path from "node:path";
import { MAIN_ACTS } from "../src/constants/script";
import { generateVoTrack } from "./lib/voGen";

generateVoTrack({
  acts: MAIN_ACTS,
  outDir: path.join(__dirname, "..", "public", "audio"),
  label: "main",
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
