import React, { useMemo } from "react";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import worldTopology from "../data/world-110m.json";
import { FLAGGED_COUNTRY_DOTS } from "../data/flaggedCountryDots";
import { COLORS } from "../constants/theme";

type Props = {
  width: number;
  height: number;
  /** Degrees of longitude rotation — animate for the slow pan. */
  rotateLambda: number;
  /** 0 -> dots hidden, 1 -> full bloom scale/opacity. Blooms as one beat, not staggered. */
  dotBloom: number;
  /** Dot uniform radius in px. */
  dotRadius?: number;
  dotColor?: string;
  /** If set, only these dot indices render (used by SC-18's zoom-to-region beat). */
  onlyIndices?: number[];
  scale?: number;
};

export const WorldMap: React.FC<Props> = ({
  width,
  height,
  rotateLambda,
  dotBloom,
  dotRadius = 6,
  dotColor = COLORS.flagged,
  onlyIndices,
  scale = 1,
}) => {
  const geographies = useMemo(() => {
    const topo = worldTopology as unknown as Topology;
    const collection = feature(
      topo,
      topo.objects.countries as GeometryCollection,
    );
    return "features" in collection ? collection.features : [collection];
  }, []);

  const dots = onlyIndices
    ? onlyIndices.map((i) => FLAGGED_COUNTRY_DOTS[i])
    : FLAGGED_COUNTRY_DOTS;

  return (
    <ComposableMap
      width={width}
      height={height}
      projection="geoOrthographic"
      projectionConfig={{
        rotate: [rotateLambda, -12, 0],
        scale: 340 * scale,
      }}
      style={{ width, height }}
    >
      <Geographies geography={geographies}>
        {({ geographies: geos }) =>
          geos.map((geo) => (
            <Geography
              key={geo.rsmKey}
              geography={geo}
              fill="#232B40"
              stroke="#3A4358"
              strokeWidth={0.5}
            />
          ))
        }
      </Geographies>
      {dots.map(([lon, lat], i) => (
        <Marker key={i} coordinates={[lon, lat]}>
          <circle
            r={dotRadius * dotBloom}
            fill={dotColor}
            opacity={dotBloom}
            style={{ filter: `drop-shadow(0 0 ${4 * dotBloom}px ${dotColor})` }}
          />
        </Marker>
      ))}
    </ComposableMap>
  );
};
