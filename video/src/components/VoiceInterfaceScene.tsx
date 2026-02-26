import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import { Phone, User, Bot, Mic, Waveform } from "lucide-react";

export const VoiceInterfaceScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slide in animation
  const slideIn = interpolate(frame, [0, 30], [100, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Pulse animation for active call
  const pulseScale = interpolate(
    frame,
    [0, 30, 60],
    [1, 1.2, 1],
    { extrapolateRight: "loop", easing: Easing.inOut(Easing.sin) }
  );

  // Waveform animation
  const bars = 20;
  const barHeights = Array.from({ length: bars }, (_, i) => {
    const offset = i * 3;
    return interpolate(
      frame + offset,
      [0, 15, 30],
      [20, 60 + Math.random() * 40, 20],
      { extrapolateRight: "loop", easing: Easing.inOut(Easing.sin) }
    );
  });

  // Chat messages appearing
  const message1Opacity = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const message2Opacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const message3Opacity = interpolate(frame, [130, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      {/* Phone Interface */}
      <div
        style={{
          width: 500,
          height: 800,
          background: "linear-gradient(180deg, #1e1b4b 0%, #312e81 100%)",
          borderRadius: 50,
          padding: 40,
          boxShadow: "0 50px 100px -20px rgba(0,0,0,0.5)",
          transform: `translateX(${slideIn}%)`,
          display: "flex",
          flexDirection: "column",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Status Bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            color: "rgba(255,255,255,0.7)",
            fontSize: 14,
            marginBottom: 40,
          }}
        >
          <span>9:41</span>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span>5G</span>
            <div
              style={{
                width: 25,
                height: 12,
                border: "2px solid rgba(255,255,255,0.7)",
                borderRadius: 3,
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: 2,
                  background: "white",
                  borderRadius: 1,
                  width: "70%",
                }}
              />
            </div>
          </div>
        </div>

        {/* Call Header */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginBottom: 40,
          }}
        >
          <div
            style={{
              width: 100,
              height: 100,
              borderRadius: 50,
              background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 20,
              boxShadow: `0 0 0 ${20 * pulseScale}px rgba(79, 70, 229, 0.3)`,
            }}
          >
            <Bot size={50} color="white" />
          </div>
          <span
            style={{
              fontSize: 24,
              fontWeight: 600,
              color: "white",
              marginBottom: 8,
            }}
          >
            Anna - Everlast AI
          </span>
          <span
            style={{
              fontSize: 16,
              color: "rgba(255,255,255,0.6)",
            }}
          >
            00:45
          </span>
        </div>

        {/* Chat Messages */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 16,
            padding: "20px 0",
          }}
        >
          {/* AI Message */}
          <div
            style={{
              display: "flex",
              gap: 12,
              opacity: message1Opacity,
              transform: `translateY(${(1 - message1Opacity) * 20}px)`,
            }}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 18,
                background: "#4f46e5",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Bot size={18} color="white" />
            </div>
            <div
              style={{
                background: "rgba(79, 70, 229, 0.3)",
                padding: "12px 16px",
                borderRadius: "4px 16px 16px 16px",
                color: "white",
                fontSize: 15,
                maxWidth: 280,
                lineHeight: 1.5,
              }}
            >
              Guten Tag! Ich bin Anna von Everlast Consulting. Haben Sie zwei Minuten für ein kurzes Gespräch?
            </div>
          </div>

          {/* User Message */}
          <div
            style={{
              display: "flex",
              gap: 12,
              alignSelf: "flex-end",
              opacity: message2Opacity,
              transform: `translateY(${(1 - message2Opacity) * 20}px)`,
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.15)",
                padding: "12px 16px",
                borderRadius: "16px 4px 16px 16px",
                color: "white",
                fontSize: 15,
                maxWidth: 280,
                lineHeight: 1.5,
              }}
            >
              Ja, gerne. Wir suchen gerade nach Lösungen für Lead-Qualifizierung.
            </div>
          </div>

          {/* AI Response with BANT */}
          <div
            style={{
              display: "flex",
              gap: 12,
              opacity: message3Opacity,
              transform: `translateY(${(1 - message3Opacity) * 20}px)`,
            }}
          >
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 18,
                background: "#4f46e5",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Bot size={18} color="white" />
            </div>
            <div
              style={{
                background: "rgba(79, 70, 229, 0.3)",
                padding: "12px 16px",
                borderRadius: "4px 16px 16px 16px",
                color: "white",
                fontSize: 15,
                maxWidth: 280,
                lineHeight: 1.5,
              }}
            >
              Das klingt spannend! Dürfen ich fragen, wie viele Mitarbeiter Ihr Unternehmen hat?
            </div>
          </div>
        </div>

        {/* Live Waveform */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 4,
            height: 80,
            marginBottom: 40,
          }}
        >
          {barHeights.map((height, i) => (
            <div
              key={i}
              style={{
                width: 6,
                height: `${height}%`,
                background: "linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%)",
                borderRadius: 3,
                transition: "height 0.1s ease",
              }}
            />
          ))}
        </div>

        {/* Call Controls */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 40,
          }}
        >
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 32,
              background: "rgba(255,255,255,0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
            }}
          >
            <Mic size={28} color="white" />
          </div>

          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 32,
              background: "#ef4444",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              boxShadow: "0 10px 30px -10px rgba(239, 68, 68, 0.5)",
            }}
          >
            <Phone size={28} color="white" style={{ transform: "rotate(135deg)" }} />
          </div>
        </div>
      </div>

      {/* Side Info Panel */}
      <div
        style={{
          position: "absolute",
          right: 100,
          top: "50%",
          transform: `translateY(-50%) translateX(${100 - slideIn}%))`,
          opacity: interpolate(frame, [60, 90], [0, 1]),
        }}
      >
        <div
          style={{
            background: "rgba(255,255,255,0.05)",
            backdropFilter: "blur(10px)",
            borderRadius: 20,
            padding: 30,
            border: "1px solid rgba(255,255,255,0.1)",
            maxWidth: 350,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              marginBottom: 20,
            }}
          >
            <Waveform size={24} color="#fbbf24" />
            <span
              style={{
                color: "#fbbf24",
                fontSize: 18,
                fontWeight: 600,
              }}
            >
              Live Sentiment Analysis
            </span>
          </div>

          {[
            { label: "Confidence", value: "94%", color: "#22c55e" },
            { label: "Sentiment", value: "Positiv", color: "#3b82f6" },
            { label: "Lead Score", value: "A", color: "#fbbf24" },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 0",
                borderBottom:
                  i < 2 ? "1px solid rgba(255,255,255,0.1)" : "none",
              }}
            >
              <span style={{ color: "rgba(255,255,255,0.6)", fontSize: 16 }}>
                {item.label}
              </span>
              <span
                style={{
                  color: item.color,
                  fontSize: 18,
                  fontWeight: 700,
                }}
              >
                {item.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
