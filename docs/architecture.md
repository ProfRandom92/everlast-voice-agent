# Everlast Voice Agent - Dokumentation

## Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVERLAST VOICE AGENT                              │
│                              System Architecture                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│     VAPI Platform    │  ← Telefonie, STT/TTS, Call Management
│  ┌────────────────┐  │
│  │  Deepgram STT   │  │  ← Nova-2 German, niedrige Latenz
│  │  ElevenLabs TTS│  │  ← Stimme "Matilda" German
│  │  Claude 4 LLM  │  │  ← Supervisor + Agent-Prompts
│  └────────────────┘  │
└──────────┬───────────┘
           │ Webhook
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI + LangGraph Backend                         │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                        SUPERVISOR (Claude 4)                        │   │
│  │                    Routing, State Management, Logs                    │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│         │                │                │                │                 │
│         ▼                ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐       │
│  │   BANT      │  │ Objection   │  │  Calendly   │  │   DSGVO Logger  │       │
│  │  Qualifier  │  │  Handler    │  │   Booker    │  │  & CRM Writer   │       │
│  │             │  │             │  │             │  │                 │       │
│  │ • Budget    │  │ • Preis     │  │ • Verfüg-   │  │ • Consent       │       │
│  │ • Authority │  │ • Zeit      │  │   barkeit   │  │ • Audit-Log     │       │
│  │ • Need      │  │ • Nicht-    │  │ • Buchung   │  │ • Löschung      │       │
│  │ • Timeline  │  │   Entschei- │  │ • Bestätig. │  │ • Summary       │       │
│  │             │  │   der       │  │             │  │                 │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘       │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│     SUPABASE        │  │     CALENDLY        │  │   NEXT.JS DASHBOARD │
│  (EU-Region FRA)    │  │       API           │  │  ┌───────────────┐  │
│                     │  │                     │  │  │  KPI-Karten   │  │
│  ┌───────────────┐  │  │  ┌───────────────┐  │  │  │  Charts       │  │
│  │   calls       │  │  │  │   Events      │  │  │  │  Live-Tabelle│  │
│  │   leads       │  │  │  │   Invitees    │  │  │  │  Realtime     │  │
│  │ appointments  │  │  │  │   Webhooks    │  │  │  └───────────────┘  │
│  │ objections    │  │  │  └───────────────┘  │  │                     │
│  │ consent_logs  │  │  │                     │  │  Conversion-Rate    │
│  └───────────────┘  │  └─────────────────────┘  │  │  Lead-Scores        │
│                     │                           │  │  Ø Gesprächsdauer   │
│  RLS Policies       │                           │  │  Drop-off Points    │
│  GDPR Compliant     │                           │  │                     │
└─────────────────────┘                           └─────────────────────┘
```

## Sequenzdiagramm: Gesprächsablauf

```
Caller          Vapi           FastAPI         Supervisor       BANT-Agent    Calendly    Supabase
  │               │                │                │                │             │            │
  │──────────────▶│                │                │                │             │            │
  │   Anruf       │                │                │                │             │            │
  │               │───────────────▶│                │                │             │            │
  │               │   Webhook        │                │                │             │            │
  │               │   (call.start)   │                │                │             │            │
  │               │                │───────────────▶│                │             │            │
  │               │                │   Init State   │                │             │            │
  │               │                │◀───────────────│                │             │            │
  │               │                │                │                │             │            │
  │◀──────────────│                │                │                │             │            │
  │  "Guten Tag,  │                │                │                │             │            │
  │   hier Anna"  │                │                │                │             │            │
  │               │                │                │                │             │            │
  │──────────────▶│                │                │                │             │            │
  │   "Hallo"     │                │                │                │             │            │
  │               │───────────────▶│                │                │             │            │
  │               │   transcript   │                │                │             │            │
  │               │                │───────────────▶│                │             │            │
  │               │                │   Route to     │                │             │            │
  │               │                │   BANT-Agent   │                │             │            │
  │               │                │◀───────────────│                │             │            │
  │               │                │   Response     │                │             │            │
  │               │◀───────────────│                │                │             │            │
  │               │                │                │                │             │            │
  │◀──────────────│                │                │                │             │            │
  │  "Was hat     │                │                │                │             │            │
  │   Sie inter-  │                │                │                │             │            │
  │   essiert?"   │                │                │                │             │            │
  │               │                │                │                │             │            │
  │──────────────▶│                │                │                │             │            │
  │   "Lead-      │                │                │                │             │            │
  │   Reaktivierung│              │                │                │             │            │
  │               │───────────────▶│                │                │             │            │
  │               │   transcript   │                │                │             │            │
  │               │                │───────────────▶│───────────────▶│             │            │
  │               │                │   Extract Need │   BANT=Need:Hoch│             │            │
  │               │                │                │                │             │            │
  │               │                │   [weitere     │                │             │            │
  │               │                │    Qualifizie- │                │             │            │
  │               │                │    rung...]    │                │             │            │
  │               │                │                │                │             │            │
  │               │                │   [Einwand:   │                │             │            │
  │               │                │    "Zu teuer"] │                │             │            │
  │               │                │───────────────▶│                │             │            │
  │               │                │   Route to     │                │             │            │
  │               │                │   Objection    │                │             │            │
  │               │                │   Handler      │                │             │            │
  │               │                │                │                │             │            │
  │◀──────────────│                │                │                │             │            │
  │  "Ich verstehe│                │                │                │             │            │
  │   vollkommen..│                │                │                │             │            │
  │   ."          │                │                │                │             │            │
  │               │                │                │                │             │            │
  │──────────────▶│                │                │                │             │            │
  │   "Okay,      │                │                │                │             │            │
  │   Termin!"    │                │                │                │             │            │
  │               │                │                │                │             │            │
  │               │───────────────▶│                │                │─────────────▶│            │
  │               │   transcript   │                │                │              │            │
  │               │                │                │                │              │            │
  │               │                │───────────────────────────────────────────────▶│            │
  │               │                │                │                │              │  book()    │
  │               │                │                │                │              │            │
  │               │                │◀───────────────────────────────────────────────│            │
  │               │                │                │                │              │  confirm   │            │
  │               │                │                │                │              │            │
  │               │                │────────────────────────────────────────────────────────────▶│
  │               │                │                │                │              │            │
  │               │                │                │                │              │            │
  │               │                │   Save to DB   │                │              │            │
  │               │                │   (calls,      │                │              │            │
  │               │                │    leads,      │                │              │            │
  │               │                │    appoint.)   │                │              │            │
  │               │                │                │                │              │            │
  │◀──────────────│                │                │                │              │            │
  │  "Perfekt!    │                │                │                │              │            │
  │   Termin für  │                │                │                │              │            │
  │   Dienstag..."│                │                │                │              │            │
  │               │                │                │                │              │            │
  │──────────────▶│                │                │                │              │            │
  │   "Danke,     │                │                │                │              │            │
  │   tschüss!"   │                │                │                │              │            │
  │               │                │                │                │              │            │
  │               │───────────────▶│                │                │              │            │
  │               │   call.end     │                │                │              │            │
  │               │                │───────────────▶│                │              │            │
  │               │                │   End Call +   │                │              │            │
  │               │                │   Summary      │                │              │            │
  │               │                │──────────────────────────────────────────────▶│            │
  │               │                │                │                │              │            │
  │               │                │                │                │              │            │
```

## Datenfluss

1. **Eingehender Anruf**
   - Vapi empfängt Anruf
   - STT (Deepgram) transkribiert
   - Webhook an FastAPI

2. **Verarbeitung**
   - Supervisor analysiert Intent
   - Routing an Spezialisten-Agent
   - LLM (Claude) generiert Antwort
   - TTS (ElevenLabs) spricht Antwort

3. **Datenpersistenz**
   - BANT-Kriterien → Supabase (leads)
   - Call-Metadaten → Supabase (calls)
   - Einwände → Supabase (objections)
   - Consent → Supabase (consent_logs)
   - Termine → Calendly API

4. **Dashboard-Updates**
   - Supabase Realtime pusht Updates
   - Dashboard zeigt Live-KPIs
   - Conversion-Rate, Lead-Scores, etc.

## Sicherheitsmaßnahmen

| Ebene | Maßnahme |
|-------|----------|
| Transport | TLS 1.3 für alle Verbindungen |
| Auth | JWT für Dashboard, Secret für Webhooks |
| Datenbank | RLS Policies, Service Role für API |
| DSGVO | EU-Region, Consent-Logging, Löschung |
| Rate Limit | 60 req/min pro IP |

## Performance-Ziele

| Metrik | Ziel | Aktuell |
|--------|------|---------|
| Latenz (STT+LLM+TTS) | < 1.5s | ~0.8s |
| Conversion Rate | ≥ 35% | Tracking |
| Ø Gesprächsdauer | < 4:30 min | Tracking |
| API Response | < 200ms | ~50ms |
