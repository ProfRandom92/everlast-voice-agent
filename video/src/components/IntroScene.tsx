import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { Phone, Bot, Sparkles } from "lucide-react";

interface IntroSceneProps {
  title?: string;
  subtitle?: string;
}

export const IntroScene: React.FC<IntroSceneProps> = ({
  title = "Everlast Voice Agent",
  subtitle = "AI-Powered B2B Lead Qualification",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Animation timings
  const bgProgress = interpolate(frame, [0, 60], [0, 1], {
    extrapolateRight: "clamp",
  });

  const logoScale = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.elastic(1.2),
  });

  const titleOpacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(frame, [40, 70], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const subtitleOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const badgeOpacity = interpolate(frame, [90, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const floatingY = interpolate(
    frame,
    [0, durationInFrames],
    [0, -20],
    {
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.sin),
    }
  );

  // Rotating ring animation
  const ringRotation = interpolate(frame, [0, 180], [0, 360], {
    extrapolateRight: "loop",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, #1e1b4b 0%, #4f46e5 50%, #7c3aed 100%)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {/* Animated background particles */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.3,
          backgroundImage: `radial-gradient(circle at ${20 + bgProgress * 10}% ${30 + bgProgress * 20}%, rgba(255,255,255,0.1) 0%, transparent 50%),
                           radial-gradient(circle at ${80 - bgProgress * 15}% ${70 - bgProgress * 10}%, rgba(255,255,255,0.08) 0%, transparent 40%)`,
        }}
      />

      {/* Central Logo Container */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          transform: `translateY(${floatingY}px) scale(${logoScale})`,
        }}
      >
        {/* Animated Ring */}
        <div
          style={{
            position: "absolute",
            width: 280,
            height: 280,
            border: "2px solid rgba(255,255,255,0.2)",
            borderRadius: "50%",
            transform: `rotate(${ringRotation}deg)`,
          }}
        >
          {[0, 90, 180, 270].map((deg, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                width: 12,
                height: 12,
                background: "#fbbf24",
                borderRadius: "50%",
                top: "50%",
                left: "50%",
                marginTop: -6,
                marginLeft: -6,
                transform: `rotate(${deg}deg) translateX(140px)`,
                boxShadow: "0 0 20px rgba(251, 191, 36, 0.6)",
              }}
            />
          ))}
        </div>

        {/* Logo Icon */}
        <div
          style={{
            width: 160,
            height: 160,
            background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)",
            borderRadius: 40,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 25px 50px -12px rgba(251, 191, 36, 0.5), 0 0 0 8px rgba(251, 191, 36, 0.2)",
            position: "relative",
          }}
        >
          <Phone size={80} color="#1e1b4b" strokeWidth={2} />
          <div
            style={{
              position: "absolute",
              bottom: 20,
              right: 20,
              width: 48,
              height: 48,
              background: "#4f46e5",
              borderRadius: 24,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(79, 70, 229, 0.4)",
            }}
          >
            <Bot size={28} color="white" />
          </div>
        </div>
      </div>

      {/* Title */}
      <h1
        style={{
          fontSize: 72,
          fontWeight: 800,
          color: "white",
          marginTop: 60,
          marginBottom: 0,
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          textShadow: "0 4px 30px rgba(0,0,0,0.3)",
          letterSpacing: "-0.02em",
        }}
      >
        {title}
      </h1>

      {/* Subtitle */}
      <p
        style={{
          fontSize: 32,
          color: "rgba(255,255,255,0.9)",
          marginTop: 20,
          opacity: subtitleOpacity,
          fontWeight: 400,
          letterSpacing: "0.05em",
        }}
      >
        {subtitle}
      </p>

      {/* Challenge Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginTop: 50,
          padding: "16px 32px",
          background: "rgba(255,255,255,0.1)",
          borderRadius: 16,
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255,255,255,0.2)",
          opacity: badgeOpacity,
        }}
      >
        <Sparkles size={24} color="#fbbf24" />
        <span
          style={{
            color: "white",
            fontSize: 20,
            fontWeight: 600,
          }}
        >
          Everlast Challenge 2026
        </span>
      </div>
    </AbsoluteFill>
  );
};
