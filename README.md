# "An AI Read 2.6 Million Cancer Papers" — Remotion project

Vox-style data-driven explainer, built entirely in Remotion (React/TS -> real MP4).
Two compositions share one scene library (`src/scenes/SC-*.tsx`, `src/SceneRegistry.tsx`):

- `MainVideo` — 1920x1080, ~240s
- `ShortsCut` — 1080x1920, ~58s, hard-loops via `LOOP-BOOKEND`

## Commands

```console
npm i
npm run dev                 # Remotion Studio preview
npm run generate-vo         # main VO + public/audio/timings.json
npm run generate-vo-shorts  # shorts VO + public/audio/shorts/timings.json
npx remotion render MainVideo out/main-1920x1080.mp4
npx remotion render ShortsCut out/shorts-1080x1920.mp4
```

Scene timing is driven by `public/audio/timings.json` / `public/audio/shorts/timings.json`
(see `src/utils/timeline.ts`), not by the storyboard's estimated second-markers, so
re-running `generate-vo` with real narration reflows every scene cut automatically.

## Known TODOs (proceeded without these per the task instructions)

- **ElevenLabs narration**: `ELEVENLABS_API_KEY` was not set, so `scripts/generate-vo*.ts`
  fall back to silent placeholder WAVs at the storyboard's estimated durations
  (see `scripts/lib/voGen.ts`). Set the key and re-run both `generate-vo` scripts to get
  real Adam narration and frame-accurate timing; captions (`src/utils/captions.ts`) are
  currently timed by a word-length estimate and should be replaced with real
  forced-alignment (e.g. `whisper-timestamped`) once real audio exists.
- **SC-21 microscope clip**: no stock source was provided, so the "only real-footage
  insert in the video" is not present; `src/scenes/SC-21.tsx` renders the split-scatter
  and foundation-building beats only.
- **Sub-bass drone bed**: no royalty-free asset was available. Only the SC-19 twist-gate
  heartbeat SFX (`public/audio/sfx/heartbeat-thump.wav`, synthesized via ffmpeg) is wired
  up; the continuous ducked drone bed under the rest of the VO is not implemented.

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).
