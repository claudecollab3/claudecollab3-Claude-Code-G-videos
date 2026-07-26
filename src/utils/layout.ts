import { useVideoConfig } from "remotion";
import { Aspect } from "../types";

/**
 * Shared layout numbers for a scene, derived from its declared aspect
 * rather than assumed dimensions, so scene components stay reusable
 * between MainVideo (1920x1080) and ShortsCut (1080x1920).
 */
export const useSceneLayout = (aspect: Aspect) => {
  const { width, height } = useVideoConfig();
  const isVertical = aspect === "vertical";
  // Vertical crops to a 60% centered safe zone per the shorts spec, and
  // scales base type up so the smallest caption text stays >=72pt-equivalent
  // at 1080x1920.
  const safeWidth = isVertical ? width * 0.6 : width * 0.86;
  const fontScale = isVertical ? 1.6 : 1;
  return { width, height, isVertical, safeWidth, fontScale };
};
