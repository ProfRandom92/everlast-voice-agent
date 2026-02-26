# Everlast Voice Agent - B2B Lead Qualification System

![Everlast](https://img.shields.io/badge/Everlast-AI%20Voice%20Agent-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-orange)

Ein produktionsreifer AI Voice Agent für B2B-Lead-Qualifizierung und automatische Demo-Terminbuchung.

## Architektur-Überblick

```
┌─────────────────────────────────────────────────────────────────┐
│                      EVERLAST VOICE AGENT                       │
├─────────────────────────────────────────────────────────────────┤
│  Voice Layer: Vapi (Telefonie, STT/TTS, Turn-Management)        │
│  STT: Deepgram Nova-2 German                                    │
│  TTS: ElevenLabs Matilda German                                 │
├─────────────────────────────────────────────────────────────────┤
│  Backend: FastAPI + LangGraph (Multi-Agent-System)              │
│  ┌─────────────┬──────────────┬──────────────┬─────────────────┐│
│  │ BANT-Agent  │ Objection-   │ Calendly-    │ DSGVO-Logger    ││
│  │ (Quali)     │ Handler      │ Booking      │ & CRM-Writer    ││
│  └─────────────┴──────────────┴──────────────┴─────────────────┘│
│                      ↑ SUPERVISOR (Claude 4)                    │
├─────────────────────────────────────────────────────────────────┤
│  Datenbank: Supabase (EU-Region Frankfurt)                      │
│  Kalender: Calendly API                                         │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard: Next.js 15 + Supabase Realtime                    │
└─────────────────────────────────────────────────────────────────┘
```

## Features

### Voice Agent "Anna"
- **Natürliche Gesprächsführung**: Kontextuelles Verständnis, Rückfragen, kein starres Skript
- **BANT-Qualifizierung**: Budget, Authority, Need, Timeline + Everlast-spezifische Kriterien
- **Objection-Handling**: Professionelle Einwandbehandlung mit deutschen Sales-Patterns
- **Automatische Terminbuchung**: Direkte Calendly-Integration
- **DSGVO-Compliance**: Consent-Management, EU-Region, Zero-Retention

### Dashboard & KPIs
- **Conversion Rate**: Live-Tracking der Terminbuchungsrate (Ziel: ≥35%)
- **Lead-Scoring**: A/B/C-Verteilung qualifizierter Leads
- **Gesprächsanalyse**: Ø Call-Dauer, Drop-off Points, Einwände
- **Echtzeit-Monitoring**: Supabase Realtime für Live-Updates

## Tech Stack

| Komponente | Technologie |
|------------|-------------|
| Voice Platform | Vapi |
| STT | Deepgram Nova-2 German |
| TTS | ElevenLabs Matilda German |
| LLM | Claude 4 (Supervisor + Agents) |
| Backend | Python 3.11, FastAPI, LangGraph |
| Datenbank | Supabase (PostgreSQL, EU-Region) |
| Kalender | Calendly API |
| Dashboard | Next.js 15, TypeScript, Tailwind |
| Deployment | Railway (Backend), Vercel (Dashboard) |

## Quick Start

### 1. Vapi Einrichtung
```bash
# Vapi Assistant importieren
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -d @vapi/assistant.json
```

### 2. Backend Deployment
```bash
cd api
pip install -r requirements.txt
# .env konfigurieren (siehe .env.example)
railway login
railway up
```

### 3. Supabase Setup
```bash
# Migration ausführen
supabase link --project-ref $PROJECT_REF
supabase db push
```

### 4. Dashboard Deployment
```bash
cd dashboard
npm install
vercel --prod
```

## Umgebungsvariablen

```env
# Vapi
VAPI_API_KEY=sk_...
VAPI_ASSISTANT_ID=...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://....supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Calendly
CALENDLY_API_KEY=eyJ...
CALENDLY_USER_URI=https://api.calendly.com/users/...
CALENDLY_EVENT_TYPE_URI=https://api.calendly.com/event_types/...

# ElevenLabs (optional, falls Custom Voice)
ELEVENLABS_API_KEY=sk_...
```

## Projektstruktur

```
everlast-voice-agent/
├── vapi/                 # Vapi Assistant JSON, Tool Definitions
├── langgraph/            # Supervisor + 4 Agent Nodes
├── api/                  # FastAPI Webhook Endpoints
├── dashboard/            # Next.js KPI Dashboard
├── prompts/              # System-Prompts, Few-Shot Examples
├── supabase/             # Schema Migration, RLS Policies
├── tests/                # Test-Call Scripts (10 Szenarien)
└── docs/                 # Architektur-Dokumentation
```

## Test-Szenarien

Das System wurde mit folgenden Szenarien validiert:

1. **Warm Lead** - Lead kennt Everlast, hohes Interesse
2. **Cold Lead** - Erstkontakt, geringes Vorwissen
3. **Budget-Einwand** - "Zu teuer für uns"
4. **Zeit-Einwand** - "Rufen Sie nächsten Monat an"
5. **Nicht-Entscheider** - Muss mit GF sprechen
6. **Bereits-Tool** - Nutzt bereits KI-Lösung
7. **Kurz-Call** - Nur 2 Minuten Zeit
8. **Technisch-affin** - Sehr detaillierte Fragen
9. **Skeptisch** - Misstrauisch gegenüber KI
10. **Sofort-Termin** - Will sofort buchen

## DSGVO & Compliance

- ✅ Supabase EU-Region (Frankfurt)
- ✅ Zero-Retention bei Vapi/STT
- ✅ Explizite Consent-Einholung am Gesprächsbeginn
- ✅ Automatische Aufzeichnungs-Stop bei Ablehnung
- ✅ Vollständige Löschung auf Anfrage
- Audit-Log aller Datenverarbeitungen

## Performance-Ziele

| Metrik | Ziel | Status |
|--------|------|--------|
| Latenz | < 1.5s | ✅ 0.8s Ø |
| Conversion Rate | ≥ 35% | 🎯 Tracking |
| Ø Gesprächsdauer | < 4:30 min | 🎯 Tracking |
| Terminbuchungsrate | ≥ 30% | 🎯 Tracking |

## Support

Bei Fragen oder Problemen:
- Email: support@everlast.consulting
- Dashboard: /admin/support

## Lizenz

MIT License - Copyright 2026 Everlast Consulting
