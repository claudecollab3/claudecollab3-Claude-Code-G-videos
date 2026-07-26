import { loadFont as loadBarlowCondensed } from "@remotion/google-fonts/BarlowCondensed";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

const { fontFamily: numeralFontFamily } = loadBarlowCondensed("normal", {
  weights: ["500", "700"],
});
const { fontFamily: bodyFontFamily } = loadInter("normal", {
  weights: ["400", "600", "800"],
});

export const LOADED_FONTS = {
  numeral: numeralFontFamily,
  body: bodyFontFamily,
};
