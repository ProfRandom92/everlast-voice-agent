import React from "react";
import { Sequence, useVideoConfig } from "remotion";
import { IntroScene } from "../components/IntroScene";
import { VoiceInterfaceScene } from "../components/VoiceInterfaceScene";
import { BANTFlowScene } from "../components/BANTFlowScene";
import { TechStackScene } from "../components/TechStackScene";
import { OutroScene } from "../components/OutroScene";

interface MainVideoProps {
  title: string;
  subtitle: string;
}

export const RemotionVideo: React.FC<MainVideoProps> = ({ title, subtitle }) => {
  const { fps } = useVideoConfig();

  // Scene timings (in frames at 30fps)
  const introDuration = 6 * fps;        // 0-6s
  const voiceDuration = 8 * fps;        // 6-14s
  const bantDuration = 10 * fps;        // 14-24s
  const techDuration = 4 * fps;         // 24-28s
  const outroDuration = 6 * fps;        // 28-34s

  const voiceStart = introDuration;
  const bantStart = voiceStart + voiceDuration;
  const techStart = bantStart + bantDuration;
  const outroStart = techStart + techDuration;

  return (
    <>
      <Sequence from={0} durationInFrames={introDuration}>
        <IntroScene title={title} subtitle={subtitle} />
      </Sequence>

      <Sequence from={voiceStart} durationInFrames={voiceDuration}>
        <VoiceInterfaceScene />
      </Sequence>

      <Sequence from={bantStart} durationInFrames={bantDuration}>
        <BANTFlowScene />
      </Sequence>

      <Sequence from={techStart} durationInFrames={techDuration}>
        <TechStackScene />
      </Sequence>

      <Sequence from={outroStart} durationInFrames={outroDuration}>
        <OutroScene />
      </Sequence>
    </>
  );
};
