# 🎬 Demo-Call Script: Everlast Voice Agent

**Datum:** 27.02.2026
**Agent:** Anna (Everlast Consulting)
**Szenario:** Warm Lead - Interessierter Geschäftsführer
**Ziel:** BANT-Qualifizierung + Terminbuchung
**Erwartete Dauer:** 3-4 Minuten

---

## 📞 Szenario-Setup

**Anrufer:** Max Mustermann, Geschäftsführer der Muster GmbH (25 Mitarbeiter)
**Kontext:** Hat sich die Case Study auf LinkedIn angesehen, 2 Minuten verweilt
**Stimmung:** Neugierig, offen, aber Zeitdruck
**Ergebnisziel:** Lead Score A oder B, Termin gebucht

---

## 🎭 Dialog-Script

### 1. Opening (0:00-0:30)

**Anna:**
> "Guten Tag, hier ist Anna von Everlast Consulting. Ich rufe an, weil Sie sich unsere Case Study zur Lead-Reaktivierung angesehen haben. Haben Sie zwei Minuten Zeit für ein kurzes Gespräch?"

**Max:**
> "Ja, genau. Ich hatte tatsächlich kurz reingeschaut. Was genau machen Sie da?"

---

### 2. Consent + Discovery (0:30-1:15)

**Anna:**
> "Zu Ihrer Information: Dieses Gespräch wird zur Qualitätssicherung aufgezeichnet. Ist das für Sie in Ordnung?"

**Max:**
> "Ja, kein Problem."

**Anna:**
> "Perfekt, danke. Also, wir bei Everlast helfen B2B-Unternehmen dabei, ihre Lead-Generierung mit KI zu automatisieren. Unsere Voice Agents übernehmen den ersten Kontakt, qualifizieren Interessenten und buchen qualifizierte Termine direkt in den Kalender. Was hat Sie besonders an der Case Study interessiert?"

**Max:**
> "Naja, wir haben halt das Problem, dass wir viele Anfragen bekommen, aber nicht wissen, welche wirklich relevant sind. Mein Vertriebsteam verschwendet da viel Zeit."

---

### 3. BANT Qualifizierung (1:15-2:30)

**Anna (Need):**
> "Das verstehe ich. Das ist eigentlich genau das, was wir lösen. Wie sieht denn Ihre aktuelle Lead-Generierung aus? Haben Sie viele unqualifizierte Anfragen?"

**Max:**
> "Ja, massenhaft. Über die Webseite, LinkedIn, Messen... Wir sind 25 Leute, da hat niemand Zeit für sowas."

**Anna (Authority):**
> "Vollkommen nachvollziehbar. Sind Sie als Geschäftsführer für solche Entscheidungen zuständig, oder müssen Sie das mit jemandem abstimmen?"

**Max:**
> "Nein, ich entscheide das selbst. Wenn es Sinn macht und ins Budget passt, können wir das umsetzen."

**Anna (Timeline + Budget):**
> "Sehr gut. Sie erwähnten Budget - haben Sie aktuell etwas für Digitalisierung eingeplant? Und wie dringend wäre das für Sie?"

**Max:**
> "Wir haben gerade das neue Quartal gestartet und Budget für Optimierung frei. Würde sagen, 10-15k sind möglich. Und dringend... ja, ich würde gerne in den nächsten 4-6 Wochen was umsetzen."

---

### 4. Pitch + Objection Handling (2:30-3:15)

**Anna:**
> "Das klingt wirklich nach einem guten Fit. Genau für solche Situationen haben wir unsere Voice Agents entwickelt. Typische Ergebnisse unserer Kunden: 60-80% Zeitersparnis im Vertrieb und 3-5x mehr qualifizierte Leads. Die Investition amortisiert sich meist innerhalb von 2-3 Monaten."

**Max:**
> "Hm, klingt gut, aber... wir haben schon ein CRM-System. Funktioniert das damit?"

**Anna (Objection - Bereits Lösung):**
> "Super, dass Sie schon ein CRM haben! Das ist keine Konkurrenz, sondern ergänzt sich ideal. Wir integrieren uns nahtlos in bestehende Systeme wie Salesforce, HubSpot oder Pipedrive. Der Agent arbeitet VOR dem CRM - er qualifiziert die Leads und spielt nur die wirklich relevanten ins CRM ein. Was nutzen Sie aktuell?"

**Max:**
> "Wir haben HubSpot. Das wäre also möglich?"

**Anna:**
> "Absolut! HubSpot ist eine unserer Standard-Integrationen. Das Setup dauert normalerweise nur 1-2 Tage."

---

### 5. Closing + Terminbuchung (3:15-3:45)

**Anna:**
> "Max, basierend auf unserem Gespräch glaube ich wirklich, dass wir Ihnen helfen können. Wären Sie offen für einen kurzen Demo-Termin? Ich kann direkt einen Termin mit einem unserer Berater für Sie reservieren – dauert nur eine Minute."

**Max:**
> "Ja, warum nicht. Wann wäre das möglich?"

**Anna:**
> "Prima! Welcher Tag würde Ihnen diese Woche am besten passen - Mittwoch oder Donnerstag?"

**Max:**
> "Donnerstag wäre besser."

**Anna:**
> "Perfekt. Morgens, mittags oder nachmittags?"

**Max:**
> "Nachmittags so gegen 14:00 Uhr?"

**Anna:**
> "Ich buche das direkt für Sie. Eine Sekunde... Das sieht gut aus. Ich habe am Donnerstag um 14:00 Uhr einen Slot für Sie reserviert. Sie bekommen gleich eine E-Mail mit dem Kalendereintrag und dem Link zum Video-Call. Passt das?"

**Max:**
> "Ja, super."

---

### 6. Abschluss + DSGVO (3:45-4:00)

**Anna:**
> "Wunderbar! Dann sehen wir uns Donnerstag. Haben Sie noch Fragen, oder kann ich sonst noch etwas für Sie tun?"

**Max:**
> "Nein, passt so. Danke für den Anruf."

**Anna:**
> "Sehr gerne, Max. Ich freue mich auf unser Gespräch am Donnerstag. Bis dahin und schönen Tag noch!"

**Max:**
> "Danke, Ihnen auch. Auf Wiederhören!"

**Anna:**
> "Auf Wiederhören!"

---

## ✅ Erwartetes Ergebnis

| Metrik | Erwartung | Tatsächlich |
|--------|-----------|-------------|
| **Lead Score** | **A** | ⬜ |
| **BANT vollständig** | Ja | ⬜ |
| **Termin gebucht** | Ja | ⬜ |
| **Sentiment** | Positiv → Begeistert | ⬜ |
| **Dauer** | 3:30-4:00 Min | ⬜ |
| **Objections überwunden** | 1/1 | ⬜ |

---

## 🔧 Backend-Validierung

Nach dem Call prüfen:

```sql
-- Call wurde geloggt
SELECT * FROM calls
WHERE phone_number = '+491234567890'
ORDER BY created_at DESC LIMIT 1;

-- Lead wurde mit Score A angelegt
SELECT * FROM leads
WHERE phone_number = '+491234567890'
ORDER BY created_at DESC LIMIT 1;

-- Termin wurde gebucht
SELECT * FROM appointments
WHERE phone_number = '+491234567890'
ORDER BY created_at DESC LIMIT 1;

-- Call Summary mit BANT-Daten
SELECT * FROM call_summaries
WHERE phone_number = '+491234567890'
ORDER BY created_at DESC LIMIT 1;
```

---

## 📊 KPI-Impact

Nach diesem Demo-Call sollte das Dashboard zeigen:
- **Total Calls:** +1
- **Conversion Rate:** Erhöht
- **Appointments:** +1
- **Lead Score A:** +1
- **Sentiment Trend:** Positiv

---

**Notizen für Aufzeichnung:**
- Natürliche Sprechweise, nicht zu schnell
- Kurze Pausen nach Fragen lassen
- Empathie bei Objection zeigen
- Freundlicher Abschluss mit Namen
