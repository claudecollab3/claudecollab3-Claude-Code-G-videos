import React from 'react';
import {COLORS} from '../theme';
import {PaperShape} from './PaperShape';
import {useStopMotionJitter} from './useStopMotionJitter';

/**
 * A stylized flat-roofed data-center warehouse: body + roof condenser units
 * + window slits, each its own paper cutout layer so the torn edges and
 * grain never repeat identically between pieces.
 */
export const DataCenterBuilding: React.FC<{
  seed: number;
  width?: number;
  height?: number;
  dim?: boolean;
  style?: React.CSSProperties;
}> = ({seed, width = 620, height = 520, dim = false, style}) => {
  const jitter = useStopMotionJitter(seed, {holdFrames: 3, posAmp: 1.2, rotAmp: 0.15});
  const bodyColor = dim ? COLORS.paperKraftDeep : COLORS.paperKraftDark;
  const roofColor = dim ? COLORS.charcoal : COLORS.paperKraftDeep;

  const unitCount = 5;
  const unitW = width * 0.1;
  const unitGap = (width - unitCount * unitW) / (unitCount + 1);

  const windowRows = 3;
  const windowCols = 6;
  const winW = width * 0.06;
  const winH = height * 0.05;
  const winPadX = width * 0.1;
  const winPadTop = height * 0.32;
  const winGapX = (width - winPadX * 2 - windowCols * winW) / (windowCols - 1);
  const winGapY = height * 0.09;

  return (
    <div style={{position: 'relative', width, height, transform: jitter.transform, ...style}}>
      <PaperShape
        seed={seed}
        width={width}
        height={height * 0.62}
        style={{position: 'absolute', left: 0, bottom: 0}}
        tornStrength={6}
        shadow={{dx: 10, dy: 16, blur: 14, opacity: 0.35}}
      >
        <rect x={4} y={4} width={width - 8} height={height * 0.62 - 8} fill={bodyColor} rx={3} />
      </PaperShape>

      <PaperShape
        seed={seed + 1}
        width={width * 1.02}
        height={height * 0.1}
        style={{position: 'absolute', left: -width * 0.01, top: height * 0.34}}
        tornStrength={5}
        shadow={{dx: 6, dy: 8, blur: 8, opacity: 0.28}}
      >
        <rect x={4} y={4} width={width * 1.02 - 8} height={height * 0.1 - 8} fill={roofColor} rx={2} />
      </PaperShape>

      {new Array(unitCount).fill(0).map((_, i) => (
        <PaperShape
          key={i}
          seed={seed + 10 + i}
          width={unitW}
          height={height * 0.14}
          style={{
            position: 'absolute',
            left: unitGap + i * (unitW + unitGap),
            top: height * 0.15,
          }}
          tornStrength={4}
          shadow={{dx: 4, dy: 6, blur: 5, opacity: 0.3}}
        >
          <rect x={3} y={3} width={unitW - 6} height={height * 0.14 - 6} fill={roofColor} rx={2} />
        </PaperShape>
      ))}

      {new Array(windowRows * windowCols).fill(0).map((_, i) => {
        const row = Math.floor(i / windowCols);
        const col = i % windowCols;
        return (
          <PaperShape
            key={i}
            seed={seed + 40 + i}
            width={winW}
            height={winH}
            style={{
              position: 'absolute',
              left: winPadX + col * (winW + winGapX),
              top: winPadTop + row * (winH + winGapY),
            }}
            tornStrength={2.5}
            grainOpacity={0.1}
            shadow={false}
          >
            <rect width={winW} height={winH} fill={dim ? '#141210' : COLORS.charcoal} opacity={dim ? 0.5 : 0.85} />
          </PaperShape>
        );
      })}
    </div>
  );
};
