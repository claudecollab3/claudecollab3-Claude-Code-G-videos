import React from "react";
import { SceneProps } from "./types";
import { Placeholder } from "./scenes/Placeholder";
import { LoopBookend } from "./scenes/LoopBookend";
import { SC01 } from "./scenes/SC-01";
import { SC02 } from "./scenes/SC-02";
import { SC03 } from "./scenes/SC-03";
import { SC04 } from "./scenes/SC-04";
import { SC05 } from "./scenes/SC-05";
import { SC06 } from "./scenes/SC-06";
import { SC07 } from "./scenes/SC-07";
import { SC08 } from "./scenes/SC-08";
import { SC09 } from "./scenes/SC-09";
import { SC10 } from "./scenes/SC-10";
import { SC11 } from "./scenes/SC-11";
import { SC12 } from "./scenes/SC-12";
import { SC13 } from "./scenes/SC-13";
import { SC14 } from "./scenes/SC-14";
import { SC15 } from "./scenes/SC-15";
import { SC16 } from "./scenes/SC-16";
import { SC17 } from "./scenes/SC-17";
import { SC18 } from "./scenes/SC-18";
import { SC19 } from "./scenes/SC-19";
import { SC20 } from "./scenes/SC-20";
import { SC21 } from "./scenes/SC-21";
import { SC22 } from "./scenes/SC-22";
import { SC23 } from "./scenes/SC-23";
import { SC24 } from "./scenes/SC-24";

export const SCENE_COMPONENTS: Record<string, React.FC<SceneProps>> = {
  "SC-01": SC01,
  "SC-02": SC02,
  "SC-03": SC03,
  "SC-04": SC04,
  "SC-05": SC05,
  "SC-06": SC06,
  "SC-07": SC07,
  "SC-08": SC08,
  "SC-09": SC09,
  "SC-10": SC10,
  "SC-11": SC11,
  "SC-12": SC12,
  "SC-13": SC13,
  "SC-14": SC14,
  "SC-15": SC15,
  "SC-16": SC16,
  "SC-17": SC17,
  "SC-18": SC18,
  "SC-19": SC19,
  "SC-20": SC20,
  "SC-21": SC21,
  "SC-22": SC22,
  "SC-23": SC23,
  "SC-24": SC24,
  "LOOP-BOOKEND": LoopBookend,
};

export const getSceneComponent = (id: string): React.FC<SceneProps> => {
  const Component = SCENE_COMPONENTS[id];
  if (Component) return Component;
  const Fallback: React.FC<SceneProps> = (props) => <Placeholder id={id} {...props} />;
  Fallback.displayName = `Placeholder(${id})`;
  return Fallback;
};
