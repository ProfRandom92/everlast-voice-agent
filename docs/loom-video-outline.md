# 🎥 Loom-Video Outline: Everlast Voice Agent

**Titel:** "Everlast Voice Agent - AI-Powered Lead Qualification in Action"
**Zielgruppe:** Potenzielle Kunden, Investoren, Tech-Community
**Länge:** 3-4 Minuten
**Sprecher:** Claude / Entwickler
**Datum:** 27.02.2026

---

## 🎯 Video-Struktur

### Teil 1: Hook (0:00-0:30)

**Visual:** Schneller Schnitt - Logo, dann Voice Agent Interface
**Audio:** "Was wenn Ihr Vertriebsteam nur noch mit qualifizierten Leads spricht?"

**Szenen:**
- [ ] Everlast Logo-Animation (2 Sek)
- [ ] Schnelle Schnitte: Telefon klingelt → Anruf angenommen → Kalender geöffnet
- [ ] Text-Overlay: "80% weniger Zeitverschwendung"

**Sprechertext:**
> "In 4 von 5 Sales-Calls verschwendet Ihr Team Zeit mit unqualifizierten Interessenten. Was wenn KI das übernehmen könnte - natürlich, empathisch und auf Deutsch?"

---

### Teil 2: Das Problem (0:30-1:00)

**Visual:** Split-Screen - Traditioneller vs. Automatisierter Prozess
**Audio:** Erklärung der Pain Points

**Links:**
- Manuelle Lead-Qualifizierung
- Zeitintensive Erstgespräche
- Keine Standardisierung

**Rechts:**
- Unser Voice Agent Konzept
- 24/7 Verfügbarkeit
- Automatische Terminbuchung

**Sprechertext:**
> "Klassische Lead-Qualifizierung ist zeitaufwändig und unzuverlässig. Vertriebsmitarbeiter verlieren Stunden mit Anrufen, die nie konvertieren. Die Folge: Frustration, hohe Kosten, verpasste Chancen."

---

### Teil 3: Die Lösung (1:00-2:00)

**Visual:** Architektur-Diagramm + Live-Demo Call
**Audio:** Technische Erklärung + Live-Dialog

**Szenen:**
- [ ] Architektur-Überblick (LangGraph Multi-Agent)
- [ ] Supervisor routing zu spezialisierten Agents
- [ ] BANT Qualifier, Objection Handler, Calendly Booker

**Diagramm:**
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Anrufer   │────▶│    Vapi      │────▶│  FastAPI    │
└─────────────┘     │  (Voice AI)  │     └─────────────┘
                    └──────────────┘            │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Termin     │◀────│ LangGraph    │◀────│  Supervisor │
│  gebucht    │     │  Multi-Agent │     │   Router    │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
         ┌─────────┬──────┴──────┬─────────┐
         ▼         ▼             ▼         ▼
    ┌────────┐ ┌────────┐   ┌────────┐ ┌────────┐
    │  BANT  │ │Object. │   │Calendly│ │ DSGVO  │
    │Qualif. │ │Handler │   │ Booker │ │ Logger │
    └────────┘ └────────┘   └────────┘ └────────┘
```

**Sprechertext:**
> "Unsere Lösung: Ein Multi-Agent-System auf Basis von LangGraph. Ein Supervisor-Agent analysiert jede Gesprächsphase und routet zu spezialisierten Agents: Der BANT-Qualifier erfasst Budget, Authority, Need und Timeline. Der Objection-Handler nutzt das LAER-Framework. Der Calendly-Booker vereinbart Termine. Alles in natürlicher, flüssiger Konversation."

---

### Teil 4: Live Demo (2:00-3:00)

**Visual:** Aufgezeichneter Call + Real-time Dashboard
**Audio:** Original-Dialog mit Voice-Over Kommentar

**Szenen:**
- [ ] Anruf beginnt: Anna begrüßt Max
- [ ] BANT-Qualifizierung läuft
- [ ] Objection handling ("Wir haben schon ein CRM")
- [ ] Terminbuchung erfolgreich
- [ ] Dashboard-Update in Real-time

**Sprechertext (während Demo):**
> "Hier sehen wir Anna in Aktion. Sie spricht natürlich, stellt Rückfragen, erfasst BANT-Kriterien. Beim Einwand bleibt sie professionell und findet einen Lösungsansatz. Nach 3 Minuten ist der Termin gebucht - und das Dashboard aktualisiert sich automatisch mit Lead Score A."

**Dashboard-Zeigen:**
- Total Calls: +1
- Conversion Rate: 85%
- Appointment gebucht
- Lead Score Distribution

---

### Teil 5: Technologie-Stack (3:00-3:30)

**Visual:** Tech-Stack Icons + Code-Snippets
**Audio:** Kurze technische Tiefe

**Stack:**
```
Voice:       Vapi → Deepgram (STT) + ElevenLabs (TTS)
AI:          Anthropic Claude 4 (LLM)
Orchestration: LangGraph (Multi-Agent)
Backend:     FastAPI + Python
Database:    Supabase (PostgreSQL)
Dashboard:   Next.js + Recharts
Deployment:  Railway (EU) + Vercel
```

**Sprechertext:**
> "Technisch setzen wir auf bewährte Komponenten: Vapi für Voice, Claude für das Language Model, LangGraph für die Agent-Orchestrierung. Das ganze läuft auf Railway in der EU - DSGVO-konform. Das Dashboard zeigt Echtzeit-KPIs."

---

### Teil 6: CTA (3:30-4:00)

**Visual:** Logo + URL + QR-Code
**Audio:** Call-to-Action

**Sprechertext:**
> "Wenn Sie Ihr Vertriebsteam entlasten und mehr qualifizierte Leads generieren wollen, let's talk. Der Everlast Voice Agent ist production-ready. Besuchen Sie everlast-voice-agent-production.up.railway.app für eine Live-Demo oder buchen Sie direkt einen Termin. Danke fürs Zuschauen!"

**End-Screen:**
- Everlast Consulting Logo
- URL: https://everlast-voice-agent-production.up.railway.app
- Dashboard Vorschau
- "Book a Demo" Button

---

## 🛠️ Produktions-Checkliste

### Vor Aufnahme:
- [ ] Script auswendig gelernt/gelesen
- [ ] Demo-Call vorab aufgezeichnet
- [ ] Dashboard-Daten vorbereitet
- [ ] Architektur-Diagramm erstellt
- [ ] Screen-Recording Software bereit
- [ ] Loom Account eingerichtet

### Aufnahme:
- [ ] Mikrofon-Test OK
- [ ] Bildschirm-Auflösung 1080p+
- [ ] Demo-Call läuft smooth
- [ ] Keine Hintergrundgeräusche
- [ ] Klare Aussprache

### Post-Production:
- [ ] Schnitt nach Outline
- [ ] Übergänge smooth
- [ ] Audio-Qualität prüfen
- [ ] Untertitel hinzugefügt
- [ ] Thumbnail erstellen
- [ ] SEO-Optimierung (Titel, Beschreibung)
- [ ] Tags: #VoiceAI #LeadGeneration #B2BSales #LangGraph #ClaudeAI

---

## 📊 Erfolgsmetriken

Nach Veröffentlichung tracken:
- [ ] Views (Ziel: 100+ in 7 Tagen)
- [ ] Engagement Rate (Ziel: >10%)
- [ ] Demo-Buchungen über Video-Link
- [ ] Social Shares

---

## 🔗 Links für Video

- **Production URL:** https://everlast-voice-agent-production.up.railway.app
- **Dashboard:** https://everlast-dashboard.vercel.app
- **Health Check:** https://everlast-voice-agent-production.up.railway.app/health
- **GitHub:** [Repository URL]

---

**Aufnahme-Tipp:** Natürlich bleiben, nicht zu schnell sprechen. 2-3 Sekunden Pause nach wichtigen Punkten lassen für bessere Verständlichkeit.
