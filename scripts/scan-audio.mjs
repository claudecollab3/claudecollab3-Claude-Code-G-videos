#!/usr/bin/env node
// Regenerates src/audioManifest.json from whatever narration files exist in
// public/audio, so MainVideo.tsx can conditionally render <Audio> per segment
// without crashing when a file hasn't been supplied yet.
import {readdirSync, writeFileSync, existsSync} from 'fs';
import {fileURLToPath} from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const audioDir = path.join(__dirname, '..', 'public', 'audio');
const outFile = path.join(__dirname, '..', 'src', 'audioManifest.json');

const manifest = {};
if (existsSync(audioDir)) {
  for (const file of readdirSync(audioDir)) {
    if (/\.(mp3|wav|m4a|ogg)$/i.test(file)) {
      const id = file.replace(/\.(mp3|wav|m4a|ogg)$/i, '');
      manifest[id] = `audio/${file}`;
    }
  }
}

writeFileSync(outFile, JSON.stringify(manifest, null, 2) + '\n');
console.log(`Wrote ${Object.keys(manifest).length} entries to ${outFile}`);
