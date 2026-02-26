# 🤖 Everlast Voice Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black.svg)](https://nextjs.org/)

> **AI Voice Agent für B2B Lead-Qualifizierung**
> Ein produktionsreifer Voice Agent, der 24/7 eingehende Anrufe entgegennimmt, Leads nach BANT-Kriterien qualifiziert und automatisch Demo-Termine bucht.

```mermaid
graph TB
    subgraph "Voice Layer"
        VAPI[Vapi Platform]
        STT[Deepgram Nova-2]
        TTS[ElevenLabs Matilda]
    end

    subgraph "AI Brain"
        SUP[Supervisor<br/>Claude 4]
        BANT[BANT Qualifier]
        OBJ[Objection Handler]
        CAL[Calendly Booker]
        DSG[DSGVO Logger]
    end

    subgraph "Data Layer"
        SB[(Supabase EU)]
        CALAPI[Calendly API]
    end

    VAPI <-- Webhook --> SUP
    STT -- Transcript --> SUP
    SUP -- Response --> TTS
    SUP --> BANT
    SUP --> OBJ
    SUP --> CAL
    SUP --> DSG
    BANT --> SB
    CAL --> CALAPI
    DSG --> SB
```

## ✨ Features

### 🎯 Core Capabilities
- **Natürliche Gesprächsführung** - Kontextuelles Verständnis, Rückfragen, kein starres Skript
- **BANT-Qualifizierung** - Budget, Authority, Need, Timeline + Everlast-spezifische Kriterien
- **Objection-Handling** - Professionelle Einwandbehandlung mit deutschen Sales-Patterns
- **Automatische Terminbuchung** - Direkte Calendly-Integration
- **DSGVO-Compliance** - Consent-Management, EU-Region, Zero-Retention

### 🧠 AI Architecture
```mermaid
flowchart TB
    subgraph "Supervisor Agent"
        S[Claude 4 Supervisor]
        S -->|Route| A1
        S -->|Route| A2
        S -->|Route| A3
        S -->|Route| A4
    end

    subgraph "Specialized Agents"
        A1[BANT Qualifier]
        A2[Objection Handler]
        A3[Calendly Booker]
        A4[DSGVO Logger]
    end

    subgraph "State Management"
        CP[(Checkpointer)]
        S <-->|Read/Write| CP
    end

    style S fill:#4f46e5,color:#fff
    style A1 fill:#22c55e,color:#fff
    style A2 fill:#f59e0b,color:#fff
    style A3 fill:#3b82f6,color:#fff
    style A4 fill:#6b7280,color:#fff
```

### 📊 Real-time Dashboard
- **Conversion Rate** - Live-Tracking der Terminbuchungsrate (Ziel: ≥35%)
- **Lead-Scoring** - A/B/C-Verteilung qualifizierter Leads
- **Gesprächsanalyse** - Ø Call-Dauer, Drop-off Points, Einwände
- **Sentiment-Tracking** - Echtzeit-Emotionsanalyse

## 🏗️ Architecture

```mermaid
graph LR
    subgraph "Frontend"
        D[Next.js 15 Dashboard]
        D -->|Realtime| SB
    end

    subgraph "Backend"
        F[FastAPI]
        LG[LangGraph]
        CP[Checkpointer]
        F --> LG
        LG --> CP
    end

    subgraph "Voice Platform"
        V[Vapi]
        DG[Deepgram STT]
        EL[ElevenLabs TTS]
        V --> DG
        V --> EL
    end

    subgraph "Data Layer"
        SB[(Supabase)]
        CL[Calendly API]
    end

    V -->|Webhook| F
    F -->|Store| SB
    F -->|Book| CL
    D -->|Query| SB
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Railway CLI: `npm install -g @railway/cli`
- Vercel CLI: `npm install -g vercel`
- Supabase CLI: `npm install -g supabase`

### Installation

```bash
# Clone repository
git clone https://github.com/ProfRandom92/everlast-voice-agent.git
cd everlast-voice-agent

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
cd api && pip install -r requirements.txt
cd ../dashboard && npm install
```

### Deployment

```bash
# Deploy backend
cd api
railway login
railway up

# Deploy dashboard
cd ../dashboard
vercel --prod

# Push database schema
supabase login
supabase db push
```

## 📖 Documentation

- [Architecture](docs/architecture.md) - System architecture and data flow
- [Deployment](DEPLOY.md) - Detailed deployment guide
- [Demo Script](docs/demo-script.md) - Demo call script
- [Test Scenarios](tests/scenarios.md) - 10 test scenarios

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VAPI_API_KEY` | Vapi API key | ✅ |
| `ANTHROPIC_API_KEY` | Claude API key | ✅ |
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | ✅ |
| `CALENDLY_API_KEY` | Calendly API key | ✅ |
| `ELEVENLABS_API_KEY` | ElevenLabs API key (optional) | ❌ |

## 📊 Monitoring

### Health Check
```bash
curl https://everlast-voice-agent-production.up.railway.app/health
```

### Dashboard
Access the real-time dashboard at: `https://everlast-dashboard.vercel.app`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Vapi](https://vapi.ai/) for voice infrastructure
- [LangGraph](https://langchain-ai.github.io/langgraph/) for agent orchestration
- [Claude](https://anthropic.com/claude) for LLM capabilities
- [Supabase](https://supabase.com/) for database infrastructure

---

<div align="center">

**[⬆ Back to Top](#-everlast-voice-agent)**

Made with ❤️ by the Everlast Team

</div>
