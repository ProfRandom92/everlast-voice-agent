# Test Szenarien für Everlast Voice Agent
# 10 realistische Gesprächsszenarien zur Validierung

---

## SZENARIO 1: WARM LEAD (Qualifizierung A)
**Beschreibung:** Lead kennt Everlast, hohes Interesse, alle BANT-Kriterien positiv

**Gesprächsverlauf:**
```
Agent: Guten Tag, hier ist Anna von Everlast Consulting...
Lead: Ah ja, ich habe Ihre Case Study gelesen. Sehr interessant!
Agent: Freut mich! Was hat Sie besonders angesprochen?
Lead: Diese Lead-Reaktivierung - wir haben da wirklich viele alte Kontakte.
Agent: Wie viele Mitarbeiter sind Sie denn?
Lead: Wir sind 45 Leute im Vertrieb.
Agent: Und sind Sie für solche Entscheidungen zuständig?
Lead: Ja, ich bin der GF.
Agent: Haben Sie Budget für KI-Projekte eingeplant?
Lead: Ja, wir haben 50k€ frei für dieses Jahr.
Agent: Wann würden Sie starten wollen?
Lead: So schnell wie möglich, am besten nächsten Monat.
Agent: Perfekt! Dann buche ich Ihnen einen Termin...
```

**Erwartetes Ergebnis:**
- Lead-Score: A
- Budget: Ja
- Authority: Entscheider
- Need: Hoch
- Timeline: Sofort
- Termin: Gebucht

---

## SZENARIO 2: COLD LEAD (Qualifizierung C)
**Beschreibung:** Erstkontakt, geringes Vorwissen, allgemeines Interesse

**Gesprächsverlauf:**
```
Agent: Guten Tag, hier ist Anna von Everlast Consulting...
Lead: Everlast? Nie gehört. Was machen Sie?
Agent: Wir helfen Unternehmen mit KI-Automatisierung...
Lead: Ah okay. Und warum rufen Sie an?
Agent: Sie haben sich unsere Case Study angesehen...
Lead: Ehrlich gesagt, ich erinnere mich nicht. Aber erzählen Sie mal.
Agent: Gerne! Wie groß ist Ihr Unternehmen?
Lead: Wir sind 8 Leute.
Agent: Und wer entscheidet über solche Dinge?
Lead: Das müssen wir intern besprechen.
Agent: Haben Sie aktuell Budget für Beratung?
Lead: Nicht wirklich eingeplant, aber wir schauen mal.
```

**Erwartetes Ergebnis:**
- Lead-Score: C
- Budget: Unklar/Nein
- Authority: Keine Entscheidungsbefugnis
- Need: Mittel
- Timeline: Unklar
- Termin: Rückruf vereinbart

---

## SZENARIO 3: BUDGET-EINWAND
**Beschreibung:** Lead ist interessiert, hat aber Budget-Bedenken

**Gesprächsverlauf:**
```
Agent: ...wären Sie offen für ein Gespräch?
Lead: Klingt interessant, aber wir haben gerade kein Budget.
Agent: Das verstehe ich. Dürfen ich fragen, in welcher Größenordnung Sie dachten?
Lead: Naja, KI-Beratung ist ja bestimmt teuer.
Agent: Viele unserer Kunden hatten anfangs ähnliche Bedenken. Was wir sehen:
       Die Amortisation erfolgt typischerweise in 8-12 Wochen.
Lead: Wirklich? Wie funktioniert das?
Agent: Durch die Zeitersparnis allein...
[Einwand wird überwunden]
Lead: Okay, das klingt anders als erwartet. Wann können wir sprechen?
```

**Erwartetes Ergebnis:**
- Einwand: Überwunden
- Lead-Score: B
- Termin: Gebucht

---

## SZENARIO 4: ZEIT-EINWAND
**Beschreibung:** Lead hat Interesse aber keine Zeit

**Gesprächsverlauf:**
```
Agent: ...haben Sie zwei Minuten Zeit?
Lead: Gerade absolut nicht, wir haben Produktionsstress.
Agent: Verstehe vollkommen. Wann wäre ein besserer Zeitpunkt?
Lead: Rufen Sie nächste Woche an.
Agent: Gerne! Wäre Montag oder Dienstag besser?
Lead: Dienstag.
Agent: Vormittags oder Nachmittags?
Lead: Lieber Nachmittag.
Agent: Perfekt. Dann rufe ich Dienstag gegen 14 Uhr an. Oder soll ich einen Termin reservieren?
Lead: Ja, Termin ist besser.
Agent: Ich habe Dienstag 14:30 Uhr frei...
```

**Erwartetes Ergebnis:**
- Einwand: Überwunden
- Rückruf-Termin: Gebucht
- Lead-Score: B

---

## SZENARIO 5: NICHT-ENTSCHEIDER
**Beschreibung:** Lead ist Assistent/in, muss mit GF sprechen

**Gesprächsverlauf:**
```
Agent: ...sind Sie für KI-Entscheidungen zuständig?
Lead: Nein, das müsste mein Chef entscheiden.
Agent: Verstehe. Darf ich fragen: Was würde ihn besonders interessieren?
Lead: Er ist sehr pragmatisch, will ROI sehen.
Agent: Perfekt! Dann stelle ich die passenden Zahlen zusammen.
       Gibt es eine Möglichkeit, dass wir gemeinsam mit ihm sprechen?
Lead: Ich kann ihn fragen.
Agent: Wäre super. Oder könnten Sie mir seine Nummer geben?
Lead: Lieber nicht, ich leite es weiter.
Agent: In Ordnung. Wann erfahre ich denn, ob er Zeit hat?
Lead: Rufen Sie Freitag an.
```

**Erwartetes Ergebnis:**
- Authority: Keine Entscheidungsbefugnis
- Einwand: Teilweise überwunden
- Rückruf: Vereinbart
- Lead-Score: C

---

## SZENARIO 6: BEREITS-TOOL
**Beschreibung:** Nutzt bereits ChatGPT/andere KI-Lösung

**Gesprächsverlauf:**
```
Agent: ...wo sehen Sie Potenzial für Automatisierung?
Lead: Wir nutzen schon ChatGPT für Texte.
Agent: Das ist großartig! Viele unserer Kunden ergänzen das.
       Was genau machen Sie mit ChatGPT?
Lead: Hauptsächlich Marketing-Texte.
Agent: Und wie läuft die Lead-Qualifizierung? Auch automatisiert?
Lead: Nein, das machen wir noch manuell.
Agent: Ah, da sehe ich Potenzial! Unsere Voice Agents übernehmen genau das...
Lead: Stimmt, das haben wir nicht.
Agent: Wäre das etwas für einen kurzen Austausch?
```

**Erwartetes Ergebnis:**
- Einwand: Überwunden (Positionierung als Ergänzung)
- Need: Hoch (neuer Bedarf identifiziert)
- Lead-Score: B

---

## SZENARIO 7: KURZ-CALL (2 Minuten)
**Beschreibung:** Lead hat nur sehr wenig Zeit

**Gesprächsverlauf:**
```
Agent: ...haben Sie zwei Minuten?
Lead: Genau zwei Minuten, dann muss ich in einen Termin.
Agent: Verstanden. Kurz: Sie haben unsere Case Study gelesen - passt das zu Ihnen?
Lead: Könnte passen, aber ich habe wirklich keine Zeit jetzt.
Agent: Kein Problem. Ein Satz: Was ist Ihr größter Schmerzpunkt?
Lead: Alte Leads, die nicht reagieren.
Agent: Genau dafür haben wir die Lösung. Dürfen ich Sie Dienstag 14 Uhr anrufen?
Lead: Ja, passt.
Agent: Perfekt. Schönen Tag!
```

**Erwartetes Ergebnis:**
- Call-Dauer: ~90 Sekunden
- Rückruf: Vereinbart
- Lead-Score: B (wegen klarem Bedarf)

---

## SZENARIO 8: TECHNISCH-AFFIN
**Beschreibung:** Sehr detaillierte technische Fragen

**Gesprächsverlauf:**
```
Agent: ...wir helfen mit KI-Automatisierung.
Lead: Welche LLMs nutzen Sie? GPT-4 oder Claude?
Agent: Wir nutzen Claude für die Gesprächsführung...
Lead: Warum nicht GPT-4? Und wie ist die Latenz?
Agent: Gute Frage! Claude ist besser im Deutschen und hat niedrigere Latenz.
       Wir messen durchschnittlich 800ms.
Lead: Okay. Und wie ist das Training?
Agent: Wir haben vortrainierte Agents, aber individuelles Fine-Tuning ist möglich.
Lead: Interessant. Was kostet so etwas?
```

**Erwartetes Ergebnis:**
- Need: Hoch
- Budget: Unklar (warte auf Preis)
- Authority: Wahrscheinlich Entscheider (tiefes Wissen)
- Termin: Gebucht

---

## SZENARIO 9: SKEPTISCH
**Beschreibung:** Misstrauisch gegenüber KI und Verkäufern

**Gesprächsverlauf:**
```
Agent: Guten Tag, hier ist Anna...
Lead: Wieder so ein KI-Anruf? Ich kriege das ständig.
Agent: Das kann ich verstehen, es gibt viel Hype. Dürfen ich kurz erklären, warum wir anders sind?
Lead: Sie haben 30 Sekunden.
Agent: Wir veröffentlichen echte Case Studies mit echten Zahlen. Kein Hype, nur Ergebnisse.
Lead: Das sagen alle.
Agent: Stimmt. Deshalb bieten wir ein unverbindliches Erstgespräch - kein Verkauf, nur Austausch.
       Wenn es nicht passt, hören Sie nie wieder von uns.
Lead: Naja...
Agent: Was haben Sie zu verlieren? 15 Minuten, und Sie bekommen ehrliches Feedback.
Lead: Okay, Termin. Aber nur 15 Minuten.
```

**Erwartetes Ergebnis:**
- Einwand: Überwunden
- Lead-Score: C (Misstrauen bleibt)
- Termin: Gebucht

---

## SZENARIO 10: SOFORT-TERMIN
**Beschreibung:** Lead will sofort buchen, sehr enthusiastisch

**Gesprächsverlauf:**
```
Agent: ...ich rufe an wegen der Case Study.
Lead: Ja! Ich wollte sowieso mit Ihnen sprechen!
Agent: Freut mich! Was interessiert Sie besonders?
Lead: Alles! Wir müssen dringend was machen.
Agent: Erzählen Sie mir kurz: Was ist Ihre größte Herausforderung?
Lead: Wir verlieren so viele Leads, das ist frustrierend.
Agent: Wie viele Mitarbeiter sind Sie?
Lead: 80. Und ich bin der GF, also kann ich entscheiden.
Agent: Haben Sie Budget?
Lead: Ja, 100k€ sind frei. Wann können wir starten?
Agent: Ich kann Ihnen gleich einen Termin geben...
Lead: Morgen geht es?
Agent: Lassen Sie mich schauen...
```

**Erwartetes Ergebnis:**
- Lead-Score: A
- Alle BANT: Positiv
- Termin: Sofort gebucht
- Priorität: Hoch

---

## TEST-AUSWERTUNG

### Erfolgskriterien

| Kriterium | Ziel | Messung |
|-----------|------|---------|
| Conversion Rate | ≥35% | Termine gebucht / Gesamt-Calls |
| Ø Gesprächsdauer | <4:30 min | Zeit bis Terminbuchung |
| Einwand-Überwindung | ≥60% | Überwunden / Gesamt-Einwände |
| Lead-Score-Genauigkeit | ≥80% | Manuelle Prüfung |

### Test-Checkliste

- [ ] Alle 10 Szenarien durchgespielt
- [ ] Latenz gemessen (<1.5s Ziel)
- [ ] Audio-Qualität geprüft
- [ ] DSGVO-Consent dokumentiert
- [ ] Terminbuchung funktioniert
- [ ] Daten in Supabase sichtbar
- [ ] Dashboard zeigt KPIs korrekt
