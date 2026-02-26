import React from "react";
import { Composition, staticFile } from "remotion";
import { IntroScene } from "./components/IntroScene";
import { VoiceInterfaceScene } from "./components/VoiceInterfaceScene";
import { BANTFlowScene } from "./components/BANTFlowScene";
import { TechStackScene } from "./components/TechStackScene";
import { OutroScene } from "./components/OutroScene";
import { RemotionVideo as MainVideo } from "./compositions/MainVideo";

export const RemotionVideo: React.FC = () => {
  return (
    <>
      {/* Main Showcase Video - 30 seconds */}
      <Composition
        id="VoiceAgentShowcase"
        component={MainVideo}
        durationInFrames={900}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Everlast Voice Agent",
          subtitle: "AI-Powered B2B Lead Qualification",
        }}
      />

      {/* Individual Scenes for flexibility */}
      <Composition
        id="IntroScene"
        component={IntroScene}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="VoiceInterface"
        component={VoiceInterfaceScene}
        durationInFrames={240}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="BANTFlow"
        component={BANTFlowScene}
        durationInFrames={300}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="TechStack"
        component={TechStackScene}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="Outro"
        component={OutroScene}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
