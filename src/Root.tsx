import "./index.css";
import { Composition } from "remotion";
import { MainVideo, mainVideoDurationInFrames, FPS, WIDTH, HEIGHT } from "./MainVideo";
import { ShortsCut, shortsDurationInFrames, SHORTS_FPS, SHORTS_WIDTH, SHORTS_HEIGHT } from "./ShortsCut";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MainVideo"
        component={MainVideo}
        durationInFrames={mainVideoDurationInFrames()}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="ShortsCut"
        component={ShortsCut}
        durationInFrames={shortsDurationInFrames()}
        fps={SHORTS_FPS}
        width={SHORTS_WIDTH}
        height={SHORTS_HEIGHT}
      />
    </>
  );
};
