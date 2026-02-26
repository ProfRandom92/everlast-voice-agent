import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { Github, ExternalLink, Award, Sparkles } from "lucide-react";

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgProgress = interpolate(frame, [0, 60], [0, 1], {
    extrapolateRight: "clamp",
  });

  const logoScale = interpolate(frame, [20, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.elastic(1.2),
  });

  const textOpacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const ctaOpacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const floatingParticles = Array.from({ length: 20 }, (_, i) => {
    const x = Math.random() * 1920;
    const y = Math.random() * 1080;
    const delay = i * 5;
    const opacity = interpolate(
      frame,
      [delay, delay + 30, delay + 60],
      [0, 0.6, 0],
      { extrapolateRight: "loop" }
    );
    return { x, y, opacity, size: 4 + Math.random() * 4 };
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
        overflow: "hidden",
      }}
    >
      {/* Animated Particles */}
      {floatingParticles.map((particle, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: particle.x,
            top: particle.y,
            width: particle.size,
            height: particle.size,
            background: "white",
            borderRadius: "50%",
            opacity: particle.opacity,
            boxShadow: "0 0 10px rgba(255,255,255,0.8)",
          }}
        />
      ))}

      {/* Glow Effect */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(251, 191, 36, 0.3) 0%, transparent 70%)",
          transform: `scale(${1 + bgProgress * 0.5})`,
          opacity: 0.5 + bgProgress * 0.5,
        }}
      />

      {/* Logo */}
      <div
        style={{
          transform: `scale(${logoScale})`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div
          style={{
            width: 120,
            height: 120,
            borderRadius: 30,
            background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 25px 50px -12px rgba(251, 191, 36, 0.5)",
            marginBottom: 30,
          }}
        >
          <span style={{ fontSize: 60 }}>🤖</span>
        </div>
      </div>

      {/* Title */}
      <h1
        style={{
          fontSize: 64,
          fontWeight: 800,
          color: "white",
          marginTop: 20,
          marginBottom: 0,
          opacity: textOpacity,
          textShadow: "0 4px 30px rgba(0,0,0,0.3)",
          letterSpacing: "-0.02em",
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        Everlast Voice Agent
        <Sparkles size={40} color="#fbbf24" />
      </h1>

      {/* Subtitle */}
      <p
        style={{
          fontSize: 28,
          color: "rgba(255,255,255,0.9)",
          marginTop: 20,
          marginBottom: 40,
          opacity: textOpacity,
          fontWeight: 400,
        }}
      >
        Challenge 2026
      </p>

      {/* Challenge Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "16px 32px",
          background: "rgba(255,255,255,0.1)",
          borderRadius: 16,
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255,255,255,0.2)",
          opacity: textOpacity,
          transform: `translateY(${interpolate(frame, [40, 70], [20, 0])}px)`,
        }}
      >
        <Award size={24} color="#fbbf24" />
        <span
          style={{
            color: "white",
            fontSize: 18,
            fontWeight: 600,
          }}
        >
          Everlast Challenge 2026
        </span>
      </div>

      {/* CTA Buttons */}
      <div
        style={{
          display: "flex",
          gap: 20,
          marginTop: 50,
          opacity: ctaOpacity,
          transform: `translateY(${interpolate(frame, [80, 110], [20, 0])}px)`,
        }}
      >
        <a
          href="https://github.com/ProfRandom92/everlast-voice-agent"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "16px 32px",
            background: "rgba(255,255,255,0.1)",
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.2)",
            color: "white",
            textDecoration: "none",
            fontSize: 18,
            fontWeight: 600,
            transition: "all 0.3s ease",
          }}
        >
          <Github size={24} />
          GitHub Repository
        </a>

        <a
          href="https://everlast.consulting"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "16px 32px",
            background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)",
            borderRadius: 12,
            color: "#1e1b4b",
            textDecoration: "none",
            fontSize: 18,
            fontWeight: 600,
            boxShadow: "0 10px 30px -10px rgba(251, 191, 36, 0.5)",
          }}
        >
          <ExternalLink size={24} />
          everlast.consulting
        </a>
      </div>

      {/* Footer */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          opacity: interpolate(frame, [100, 130], [0, 1]),
        }}
      >
        <span
          style={{
            color: "rgba(255,255,255,0.6)",
            fontSize: 16,
          }}
        >
          Made with ❤️ for the Everlast Challenge 2026
        </span>
      </div>
    </AbsoluteFill>
  );
};
