import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync, existsSync } from "node:fs";
import { Act } from "../../src/constants/script";

const VOICE_ID_ADAM = "pNInz6obpgDQGcFmaJgB"; // ElevenLabs premade voice "Adam"

export type TimingManifest = {
  generatedAt: string;
  source: "elevenlabs" | "placeholder-silence";
  interActGapSeconds: number;
  acts: {
    id: string;
    file: string;
    durationSeconds: number;
    startSeconds: number;
  }[];
  totalSeconds: number;
};

const ffprobeDuration = (file: string): number => {
  const out = execFileSync("ffprobe", [
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
    file,
  ]).toString();
  return parseFloat(out.trim());
};

const generateSilence = (file: string, seconds: number) => {
  execFileSync("ffmpeg", [
    "-y",
    "-loglevel",
    "error",
    "-f",
    "lavfi",
    "-i",
    `anullsrc=r=44100:cl=mono`,
    "-t",
    seconds.toFixed(2),
    file,
  ]);
};

const generateViaElevenLabs = async (apiKey: string, text: string, file: string) => {
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID_ADAM}`, {
    method: "POST",
    headers: {
      "xi-api-key": apiKey,
      "Content-Type": "application/json",
      Accept: "audio/wav",
    },
    body: JSON.stringify({
      text,
      model_id: "eleven_multilingual_v2",
      voice_settings: {
        stability: 0.42,
        similarity_boost: 0.78,
        style: 0.22,
        use_speaker_boost: true,
      },
    }),
  });
  if (!res.ok) {
    throw new Error(`ElevenLabs request failed: ${res.status} ${await res.text()}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  writeFileSync(file, buf);
};

export const generateVoTrack = async (opts: {
  acts: Act[];
  outDir: string;
  interActGapSeconds?: number;
  label: string;
}) => {
  const { acts: scriptActs, outDir, interActGapSeconds = 0.4, label } = opts;
  mkdirSync(outDir, { recursive: true });
  const apiKey = process.env.ELEVENLABS_API_KEY;
  const source: TimingManifest["source"] = apiKey ? "elevenlabs" : "placeholder-silence";

  if (!apiKey) {
    console.warn(
      `[generate-vo:${label}] ELEVENLABS_API_KEY not set — writing silent placeholder WAVs ` +
        "at estimated storyboard durations. Re-run with the key set to get real narration " +
        "and frame-accurate timings.",
    );
  }

  const acts: TimingManifest["acts"] = [];
  let cursor = 0;

  for (const act of scriptActs) {
    const file = `${outDir}/${act.id}.wav`;
    if (apiKey) {
      await generateViaElevenLabs(apiKey, act.text, file);
    } else {
      generateSilence(file, act.estimatedSeconds);
    }
    const durationSeconds = existsSync(file) ? ffprobeDuration(file) : act.estimatedSeconds;
    acts.push({
      id: act.id,
      file: `audio/${label === "shorts" ? "shorts/" : ""}${act.id}.wav`,
      durationSeconds,
      startSeconds: cursor,
    });
    cursor += durationSeconds + interActGapSeconds;
  }

  const manifest: TimingManifest = {
    generatedAt: new Date().toISOString(),
    source,
    interActGapSeconds,
    acts,
    totalSeconds: cursor - interActGapSeconds,
  };

  writeFileSync(`${outDir}/timings.json`, JSON.stringify(manifest, null, 2));
  console.log(`[generate-vo:${label}] Wrote ${acts.length} act files + timings.json (source=${source}).`);
  console.log(`[generate-vo:${label}] Total VO duration: ${manifest.totalSeconds.toFixed(2)}s`);
};
