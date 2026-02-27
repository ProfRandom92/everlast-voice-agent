# 🧪 Test-Call Szenarien: Everlast Voice Agent

**Datum:** 27.02.2026
**Tester:** [Name eintragen]
**Telefonnummer:** [Vapi-Nummer eintragen]
**Ziel:** Alle 10 Szenarien durchspielen und validieren

---

## 📋 Test-Protokoll

| # | Szenario | Erwartetes Ergebnis | Ergebnis | Lead Score | ✅/❌ |
|---|----------|---------------------|----------|------------|-------|
| 1 | Warm Lead | Termin gebucht, Score A/B | | | ⬜ |
| 2 | Cold Lead | BANT erhoben, keine Buchung | | | ⬜ |
| 3 | Preis-Einwand | LAER überwunden, Termin | | | ⬜ |
| 4 | Zeit-Einwand | Alternativ-Termin gebucht | | | ⬜ |
| 5 | Nicht-Entscheider | Influencer-Infos erfasst | | | ⬜ |
| 6 | Bereits Lösung | Ergänzung verkauft | | | ⬜ |
| 7 | Kein Bedarf | Archiviert, Score N | | | ⬜ |
| 8 | Misstrauen | Trust aufgebaut | | | ⬜ |
| 9 | Abbruch | Call Summary, DSGVO | | | ⬜ |
| 10 | Wiederverbindung | Checkpoint geladen | | | ⬜ |

---

## 🎭 Detaillierte Szenarien

### Szenario 1: WARM LEAD (Ziel: Score A, Termin)
**Anrufer:** Sarah Weber, GF von Weber Consulting (40 MA)
**Kontext:** Hat sich Case Study angesehen, 5 Minuten Verweildauer
**Verhalten:** Interessiert, offen, stellt Fragen
**BANT:**
- Budget: Ja, 15k frei
- Authority: Geschäftsführerin
- Need: Hoch (Lead-Qualifizierung)
- Timeline: 1-3 Monate

**Gesprächsverlauf:**
1. ✅ Consent gegeben
2. ✅ Entdeckt Need: "Wir haben zu viele unqualifizierte Anfragen"
3. ✅ Authority bestätigt: "Ich entscheide das selbst"
4. ✅ Budget: "15k sind drin"
5. ✅ Timeline: "Würde gerne in 6-8 Wochen starten"
6. ✅ Termin gebucht

**Erwartetes Ergebnis:**
- Lead Score: **A**
- Termin: Ja
- Sentiment: Positiv → Begeistert
- Dauer: 3-4 Min

---

### Szenario 2: COLD LEAD (Ziel: Score C, kein Termin)
**Anrufer:** Hans Müller, Büro-Müller GmbH (8 MA)
**Kontext:** Auf LinkedIn gesehen, nicht aktiv geklickt
**Verhalten:** Höflich, aber zurückhaltend

**Gesprächsverlauf:**
1. ✅ Consent gegeben
2. ⚠️ Need: "Nur mal reinschauen"
3. ⚠️ Authority: "Ich muss das erst absprechen"
4. ❌ Budget: "Kein Budget eingeplant"
5. ❌ Timeline: "Nicht klar"
6. ❌ Kein Termin gebucht

**Erwartetes Ergebnis:**
- Lead Score: **C**
- Termin: Nein
- Sentiment: Neutral
- Aktion: Nur Rückruf-Termin angeboten

---

### Szenario 3: PREIS-EINWAND (Ziel: Überwunden, Termin)
**Anrufer:** Klaus Schmidt, Schmidt Digital (20 MA)
**Verhalten:** Zuerst interessiert, dann: "Das klingt aber teuer"

**Einwand-Behandlung (LAER):**
1. **Listen:** Anna hört zu
2. **Acknowledge:** "Ich verstehe, Budget ist wichtig"
3. **Explore:** "Was hätten Sie erwartet?"
4. **Respond:** ROI-Berechnung, flexible Modelle

**Erwartetes Ergebnis:**
- Objection Type: "Preis"
- Outcome: "Überwunden"
- Termin: Ja

---

### Szenario 4: ZEIT-EINWAND (Ziel: Alternativ-Termin)
**Anrufer:** Lisa Kaufmann, Kaufmann Solutions (15 MA)
**Einwand:** "Ich habe gerade keine Zeit"

**Erwartete Response:**
- Empathie zeigen
- Konkrete Alternativen: "Wann würde besser passen?"
- Rückruf-Termin reservieren

**Erwartetes Ergebnis:**
- Objection Type: "Zeit"
- Outcome: "Überwunden"
- Termin: Rückruf vereinbart

---

### Szenario 5: NICHT-ENTSCHEIDER (Ziel: Influencer erfassen)
**Anrufer:** Thomas Berger, Mitarbeiter bei Tech GmbH (100 MA)
**Statement:** "Ich bin nicht der Geschäftsführer"

**Erwartete Strategie:**
- Verständnis zeigen
- Fragen: "Was würde Ihr GF interessieren?"
- Nach Kontakt fragen: "Können Sie mich verbinden?"

**Erwartetes Ergebnis:**
- Authority: "Keine Entscheidungsbefugnis"
- Lead Score: **C**
- Notizen: GF-Infos erfasst

---

### Szenario 6: BEREITS LÖSUNG (Ziel: Ergänzung positionieren)
**Anrufer:** Maria Koch, Koch Innovation (30 MA)
**Statement:** "Wir nutzen schon ChatGPT"

**Erwartete Response:**
- Nicht abwerten: "Super, dass Sie KI nutzen!"
- Ergänzung betonen: "Wir spezialisieren uns auf Voice"
- Frage stellen: "Was fehlt Ihnen noch?"

**Erwartetes Ergebnis:**
- Objection Type: "Bereits-Lösung"
- Outcome: "Überwunden"
- Termin: Ja (Demo)

---

### Szenario 7: KEIN BEDARF (Ziel: Archivieren)
**Anrufer:** Peter Wolf, Wolf Handel (5 MA)
**Statement:** "Nein, wir brauchen das nicht. Läuft alles gut."

**Erwartete Response:**
- Respektieren: "Ich verstehe"
- Frage: "Was läuft besonders gut?"
- 6-Monats-Follow-up anbieten

**Erwartetes Ergebnis:**
- Lead Score: **N**
- Call Outcome: "Nicht interessiert"
- Next Steps: "Follow-up in 6 Monaten"

---

### Szenario 8: MISSTRAUEN (Ziel: Trust aufbauen)
**Anrufer:** Andreas Klein, Klein Security (50 MA)
**Statement:** "KI ist doch nur Hype. Roboter können nicht verkaufen."

**Erwartete Response:**
- Zustimmen: "Es gibt viel Hype, das stimmt"
- Case Studies zeigen: "Hier sind echte Ergebnisse"
- Menschliches Angebot: "Unverbindliches Gespräch mit unserem GF"

**Erwartetes Ergebnis:**
- Objection Type: "Misstrauen"
- Sentiment: Negativ → Neutral
- Termin: Vielleicht (GF-Call)

---

### Szenario 9: ABBRUCH (Ziel: Clean exit)
**Anrufer:** [Beliebig]
**Verhalten:** Legt nach 30 Sekunden auf

**Erwartetes Verhalten:**
- Anna bemerkt Abbruch
- EndCallSummary wird ausgelöst
- DSGVO: Consent-Status geloggt
- Call als "Abgebrochen" markiert

**Erwartetes Ergebnis:**
- Call Outcome: "Abgebrochen"
- Lead Score: **N**
- Duration: <1 Min
- Dashboard: +1 Call, 0% Conversion

---

### Szenario 10: WIEDERVERBINDUNG (Ziel: Kontext wiederherstellen)
**Setup:**
1. Erster Call: Warm Lead, Termin vereinbart
2. Gleiche Nummer ruft 2 Tage später wieder an
3. Checkpoint sollte geladen werden

**Erwartetes Verhalten:**
- Anna erkennt: "Hallo Herr Weber, schön wieder von Ihnen zu hören!"
- Kontext: "Wir hatten einen Termin für Donnerstag vereinbart"
- State aus Supabase-Checkpoint geladen

**Erwartetes Ergebnis:**
- BANT-Daten aus erstem Call erhalten
- Konversation fortgesetzt
- Sentiment: Positiv

---

## 🔧 Test-Durchführung

### Vorbereitung:
1. [ ] Vapi-Telefonnummer bereit
2. [ ] Dashboard geöffnet (https://everlast-dashboard.vercel.app)
3. [ ] Supabase Dashboard geöffnet
4. [ ] Test-Protokoll ausgedruckt/Ready

### Durchführung pro Szenario:
1. [ ] Anrufen
2. [ ] Rolle spielen (siehe Szenario)
3. [ ] Gespräch führen
4. [ ] Auflegen
5. [ ] 30 Sekunden warten
6. [ ] Dashboard prüfen
7. [ ] Supabase prüfen
8. [ ] Ergebnis eintragen

### Dashboard-Validierung:
```
Nach jedem Call prüfen:
□ Total Calls +1
□ Lead Score richtig zugeordnet
□ Sentiment korrekt
□ Duration sinnvoll
□ Termin gebucht (falls ja)
```

### Supabase-Validierung:
```sql
-- Nach Szenario X:
SELECT * FROM calls ORDER BY created_at DESC LIMIT 1;
SELECT * FROM leads ORDER BY created_at DESC LIMIT 1;
SELECT * FROM call_summaries ORDER BY created_at DESC LIMIT 1;
```

---

## 📊 Ergebnis-Zusammenfassung

| Metrik | Ziel | Erreicht |
|--------|------|----------|
| Tests durchgeführt | 10/10 | ⬜ |
| Conversion Rate | ≥35% | ⬜ |
| Objection Success | ≥70% | ⬜ |
| Avg Duration | 3-5 Min | ⬜ |
| Lead Score Accuracy | 100% | ⬜ |

---

## 🐍 Fehler-Log

| Szenario | Fehler | Beschreibung | Status |
|----------|--------|--------------|--------|
| | | | |

---

**Tester:** ___________________
**Datum:** ___________________
**Signatur:** ___________________

**Fazit:** ⬜ Alle Tests bestanden ⬜ Nachbesserungen nötig
