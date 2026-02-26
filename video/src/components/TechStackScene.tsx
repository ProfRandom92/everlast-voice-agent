import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";

const techStack = [
  { name: "Vapi", category: "Voice", color: "#4f46e5", icon: "📞" },
  { name: "Claude 4", category: "AI Brain", color: "#7c3aed", icon: "🧠" },
  { name: "LangGraph", category: "Orchestration", color: "#22c55e", icon: "🔄" },
  { name: "FastAPI", category: "Backend", color: "#3b82f6", icon: "⚡" },
  { name: "Next.js", category: "Dashboard", color: "#000000", icon: "▲" },
  { name: "Supabase", category: "Database", color: "#22c55e", icon: "🗄️" },
];

export const TechStackScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const containerOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        padding: 60,
        opacity: containerOpacity,
      }}
    >
      {/* Header */}
      <h2
        style={{
          fontSize: 48,
          fontWeight: 800,
          color: "white",
          marginBottom: 60,
          opacity: interpolate(frame, [10, 40], [0, 1]),
          transform: `translateY(${interpolate(frame, [10, 40], [30, 0])}px)`,
        }}
      >
        Tech Stack
      </h2>

      {/* Tech Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 30,
          maxWidth: 900,
        }}
      >
        {techStack.map((tech, index) => {
          const delay = 40 + index * 10;
          const opacity = interpolate(frame, [delay, delay + 20], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          const translateY = interpolate(
            frame,
            [delay, delay + 20],
            [50, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }
          );

          const scale = interpolate(
            frame,
            [delay, delay + 20],
            [0.8, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(1.5)) }
          );

          return (
            <div
              key={tech.name}
              style={{
                background: "rgba(255,255,255,0.05)",
                borderRadius: 24,
                padding: 30,
                border: "1px solid rgba(255,255,255,0.1)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 12,
                opacity,
                transform: `translateY(${translateY}px) scale(${scale})`,
                transition: "all 0.3s ease",
              }}
            >
              <div
                style={{
                  width: 60,
                  height: 60,
                  borderRadius: 16,
                  background: tech.color,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 28,
                  boxShadow: `0 10px 30px -10px ${tech.color}80`,
                }}
              >
                {tech.icon}
              </div>
              <span
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: "white",
                  marginTop: 8,
                }}
              >
                {tech.name}
              </span>
              <span
                style={{
                  fontSize: 14,
                  color: "rgba(255,255,255,0.5)",
                }}
              >
                {tech.category}
              </span>
            </div>
          );
        })}
      </div>

      {/* Connection Lines Animation */}
      <svg
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
        }}
      >
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4f46e5" stopOpacity="0" />
            <stop offset="50%" stopColor="#4f46e5" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#7c3aed" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </AbsoluteFill>
  );
};
