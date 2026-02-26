import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import {
  Wallet,
  Users,
  Target,
  Calendar,
  CheckCircle,
  ArrowRight,
  Bot,
  Sparkles,
} from "lucide-react";

interface BANTStepProps {
  icon: React.ReactNode;
  title: string;
  question: string;
  delay: number;
  isActive: boolean;
  isComplete: boolean;
  frame: number;
  fps: number;
}

const BANTStep: React.FC<BANTStepProps> = ({
  icon,
  title,
  question,
  delay,
  isActive,
  isComplete,
  frame,
  fps,
}) => {
  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame, [delay, delay + 15], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  const scale = isActive
    ? interpolate(
        frame,
        [0, 15],
        [1, 1.05],
        { extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) }
      )
    : 1;

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
        background: isComplete
          ? "linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%)"
          : isActive
          ? "linear-gradient(135deg, rgba(79, 70, 229, 0.3) 0%, rgba(124, 58, 237, 0.2) 100%)"
          : "rgba(255,255,255,0.05)",
        borderRadius: 20,
        padding: 24,
        border: isComplete
          ? "1px solid rgba(34, 197, 94, 0.5)"
          : isActive
          ? "1px solid rgba(79, 70, 229, 0.5)"
          : "1px solid rgba(255,255,255,0.1)",
        display: "flex",
        alignItems: "flex-start",
        gap: 16,
        transition: "all 0.3s ease",
        minWidth: 400,
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 12,
          background: isComplete
            ? "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)"
            : isActive
            ? "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)"
            : "rgba(255,255,255,0.1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        {isComplete ? (
          <CheckCircle size={24} color="white" />
        ) : (
          React.cloneElement(icon as React.ReactElement, {
            size: 24,
            color: isActive ? "white" : "rgba(255,255,255,0.5)",
          })
        )}
      </div>

      <div style={{ flex: 1 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 8,
          }}
        >
          <span
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: isComplete ? "#22c55e" : isActive ? "white" : "rgba(255,255,255,0.7)",
            }}
          >
            {title}
          </span>
          {isActive && (
            <Sparkles size={16} color="#fbbf24" />
          )}
        </div>
        <p
          style={{
            fontSize: 14,
            color: "rgba(255,255,255,0.7)",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          {question}
        </p>
      </div>
    </div>
  );
};

export const BANTFlowScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const steps = [
    {
      icon: <Wallet />,
      title: "Budget",
      question: "Haben Sie Budget für KI-Beratung?",
      delay: 30,
    },
    {
      icon: <Users />,
      title: "Authority",
      question: "Sind Sie für Entscheidungen zuständig?",
      delay: 90,
    },
    {
      icon: <Target />,
      title: "Need",
      question: "Welche Herausforderungen haben Sie aktuell?",
      delay: 150,
    },
    {
      icon: <Calendar />,
      title: "Timeline",
      question: "Wann möchten Sie starten?",
      delay: 210,
    },
  ];

  const getStepStatus = (index: number) => {
    const stepFrame = frame - steps[index].delay;
    if (stepFrame < 0) return { isActive: false, isComplete: false };
    if (stepFrame > 60) return { isActive: false, isComplete: true };
    return { isActive: true, isComplete: false };
  };

  // Progress bar
  const progress = interpolate(frame, [30, 270], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Final score animation
  const scoreOpacity = interpolate(frame, [260, 290], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scoreScale = interpolate(
    frame,
    [260, 280],
    [0.8, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.elastic(1) }
  );

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, system-ui, sans-serif",
        padding: 60,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          marginBottom: 60,
          opacity: interpolate(frame, [0, 30], [0, 1]),
          transform: `translateY(${interpolate(frame, [0, 30], [20, 0])}px)`,
        }}
      >
        <div
          style={{
            width: 60,
            height: 60,
            borderRadius: 16,
            background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Bot size={32} color="#1e1b4b" />
        </div>
        <div>
          <h2
            style={{
              fontSize: 36,
              fontWeight: 800,
              color: "white",
              margin: 0,
              marginBottom: 8,
            }}
          >
            BANT Qualification
          </h2>
          <p
            style={{
              fontSize: 18,
              color: "rgba(255,255,255,0.7)",
              margin: 0,
            }}
          >
            Automatische Lead-Qualifizierung in Echtzeit
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          width: "100%",
          maxWidth: 800,
          height: 4,
          background: "rgba(255,255,255,0.1)",
          borderRadius: 2,
          marginBottom: 60,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: "100%",
            background: "linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%)",
            borderRadius: 2,
            transition: "width 0.1s linear",
          }}
        />
      </div>

      {/* BANT Steps */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 20,
          marginBottom: 60,
        }}
      >
        {steps.map((step, index) => {
          const { isActive, isComplete } = getStepStatus(index);
          return (
            <BANTStep
              key={index}
              icon={step.icon}
              title={step.title}
              question={step.question}
              delay={step.delay}
              isActive={isActive}
              isComplete={isComplete}
              frame={frame}
              fps={fps}
            />
          );
        })}
      </div>

      {/* Final Score */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 24,
          opacity: scoreOpacity,
          transform: `scale(${scoreScale})`,
        }}
      >
        <div
          style={{
            background: "linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%)",
            border: "2px solid #22c55e",
            borderRadius: 24,
            padding: "32px 48px",
            display: "flex",
            alignItems: "center",
            gap: 20,
          }}
        >
          <div
            style={{
              width: 80,
              height: 80,
              borderRadius: 40,
              background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 40,
              fontWeight: 800,
              color: "white",
              boxShadow: "0 10px 40px -10px rgba(34, 197, 94, 0.5)",
            }}
          >
            A
          </div>
          <div>
            <div
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: "#22c55e",
                marginBottom: 4,
              }}
            >
              Lead Score: A
            </div>
            <div
              style={{
                fontSize: 16,
                color: "rgba(255,255,255,0.7)",
              }}
            >
              Heißer Lead - Termin buchen ✓
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
