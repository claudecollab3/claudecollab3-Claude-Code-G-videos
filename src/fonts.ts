import {loadFont} from '@remotion/fonts';
import {continueRender, delayRender, staticFile} from 'remotion';

export const condensedFontFamily = 'Oswald';
export const bodyFontFamily = 'Inter';

// Fonts are self-hosted in public/fonts (downloaded once from Google Fonts)
// and loaded from disk so rendering never depends on network access.
const handle = delayRender('Loading local fonts');

Promise.all([
  loadFont({
    family: condensedFontFamily,
    url: staticFile('fonts/Oswald-Variable.woff2'),
    weight: '500 700',
  }),
  loadFont({
    family: bodyFontFamily,
    url: staticFile('fonts/Inter-Variable.woff2'),
    weight: '400 700',
  }),
])
  .then(() => continueRender(handle))
  .catch((err) => {
    console.error('Font loading failed', err);
    continueRender(handle);
  });
