import React from 'react';
import {Background} from '../components/Background';
import {DataCenterBuilding} from '../components/DataCenterBuilding';
import {LightningBolt} from '../components/LightningBolt';

export const Scene1Hook: React.FC = () => {
  return (
    <Background seed="scene1">
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <DataCenterBuilding seed={1} width={680} height={560} />
      </div>

      <LightningBolt seed={301} left={130} top={80} delayFrames={4} width={70} height={340} />
      <LightningBolt seed={302} left={330} top={40} delayFrames={14} width={85} height={300} />
      <LightningBolt seed={303} left={620} top={70} delayFrames={9} width={75} height={330} />
      <LightningBolt seed={304} left={840} top={110} delayFrames={20} width={65} height={260} />
    </Background>
  );
};
