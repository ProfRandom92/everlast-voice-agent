# Calendly Integration Setup Guide

## Overview

Diese Anleitung beschreibt die Einrichtung der Calendly-Integration für den Everlast Voice Agent. Der Agent kann automatisch Demo-Termine direkt über das Telefon buchen.

## Features

- **Automatische Terminbuchung**: Vapi-Agent bucht Termine während des Gesprächs
- **Echtzeit-Verfügbarkeitsprüfung**: Zeigt nur verfügbare Slots
- **Fehlerbehandlung**: Professionelle Fehlermeldungen auf Deutsch
- **Doppelbuchungsschutz**: Verhindert Konflikte
- **Zeitzonen-Unterstützung**: Automatische Anpassung
- **SMS-Erinnerungen**: Text-Reminder an Teilnehmer

## Prerequisites

- Calendly Account (Professional oder höher für API-Zugriff)
- Calendly API Token
- Event Type URI für Voice-Agent-Buchungen

## Setup Steps

### 1. Calendly API Token erstellen

1. Melden Sie sich bei [Calendly](https://calendly.com) an
2. Gehen Sie zu **Integrations** → **API & Webhooks**
3. Klicken Sie auf **Generate New Token**
4. Geben Sie einen Namen ein: `Everlast Voice Agent`
5. Kopieren Sie den Token und speichern Sie ihn sicher

### 2. Event Type konfigurieren

1. In Calendly: Gehen Sie zu **Event Types**
2. Erstellen Sie einen neuen Event Type oder verwenden Sie einen bestehenden:
   - **Name**: z.B. "Everlast Voice Demo"
   - **Dauer**: 30 Minuten empfohlen
   - **Beschreibung**: Beschreibung für den Voice Agent
3. Notieren Sie die Event Type URI:
   - Klicken Sie auf den Event Type → **Share your link**
   - Die URI hat das Format: `https://api.calendly.com/event_types/UUID`

### 3. Environment Variables

Erstellen Sie eine `.env` Datei im Projekt-Root:

```env
# Calendly Configuration
CALENDLY_API_KEY=your_api_token_here
CALENDLY_USER_URI=https://api.calendly.com/users/YOUR_USER_ID
CALENDLY_EVENT_TYPE_URI=https://api.calendly.com/event_types/YOUR_EVENT_TYPE_UUID
CALENDLY_DEFAULT_TIMEZONE=Europe/Berlin
CALENDLY_AUTO_CONFIRM=true
```

#### Werte ermitteln:

**CALENDLY_USER_URI**:
```bash
curl -X GET https://api.calendly.com/users/me \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

Response:
```json
{
  "resource": {
    "uri": "https://api.calendly.com/users/ABC123",
    "email": "you@example.com"
  }
}
```

**CALENDLY_EVENT_TYPE_URI**:
```bash
curl -X GET "https://api.calendly.com/event_types?user=YOUR_USER_URI" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### 4. Installation

```bash
# Abhängigkeiten installieren
pip install httpx

# Oder falls requirements.txt existiert:
pip install -r requirements.txt
```

### 5. Tests durchführen

```bash
# Alle Tests ausführen
python -m pytest test_calendly.py -v

# Manuelle Tests mit Output
python test_calendly.py

# Spezifische Tests
python -m pytest test_calendly.py::test_book_appointment_success -v
```

## Vapi Integration

### Assistant Configuration

Die `bookAppointment` Function ist bereits in `vapi/assistant.json` konfiguriert:

```json
{
  "name": "bookAppointment",
  "description": "Bucht einen Demo-Termin im Calendly",
  "parameters": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "email": { "type": "string" },
      "date": { "type": "string", "description": "YYYY-MM-DD" },
      "time": { "type": "string", "description": "HH:MM" },
      "phone": { "type": "string" },
      "company": { "type": "string" },
      "notes": { "type": "string" }
    },
    "required": ["name", "email", "date", "time"]
  }
}
```

### Server Webhook URL

Stellen Sie sicher, dass die Webhook URL in Vapi konfiguriert ist:

```json
{
  "server": {
    "url": "https://your-domain.com/vapi/webhook",
    "secret": "your_webhook_secret"
  }
}
```

## API Endpoints

### Webhook Handler

Der `/vapi/webhook` Endpoint verarbeitet `bookAppointment` Function Calls:

```python
POST /vapi/webhook
Content-Type: application/json
X-Vapi-Secret: your_secret

{
  "function_call": {
    "name": "bookAppointment",
    "parameters": {
      "name": "Max Mustermann",
      "email": "max@example.com",
      "date": "2024-03-15",
      "time": "14:00",
      "company": "Muster GmbH",
      "notes": "Interesse an KI-Automatisierung"
    }
  }
}
```

### Response Format

```json
{
  "status": "appointment_booked",
  "message": "Termin wurde erfolgreich gebucht.",
  "details": {
    "success": true,
    "status": "confirmed",
    "event_uri": "https://api.calendly.com/scheduled_events/...",
    "confirmation_url": "https://calendly.com/...",
    "start_time": "2024-03-15T14:00:00+01:00",
    "end_time": "2024-03-15T14:30:00+01:00"
  }
}
```

## Error Handling

### Deutsche Fehlermeldungen

Die Integration gibt professionelle Fehlermeldungen auf Deutsch zurück:

| Error Code | Nachricht |
|------------|-----------|
| `DOUBLE_BOOKING` | "Der Termin ist leider bereits vergeben. Bitte wählen Sie einen anderen Zeitpunkt." |
| `PAST_DATE` | "Der gewählte Zeitpunkt liegt in der Vergangenheit. Bitte wählen Sie eine zukünftige Zeit." |
| `CONFIG_MISSING` | "Die Kalenderintegration ist nicht korrekt konfiguriert." |
| `VALIDATION_ERROR` | "Die eingegebenen Daten sind ungültig." |
| `API_ERROR` | "Es ist ein technischer Fehler aufgetreten. Bitte versuchen Sie es später erneut." |

### Retry-Logik

Der Client implementiert automatische Wiederholungen mit exponentiellem Backoff:
- Maximale Versuche: 3
- Initialer Delay: 1 Sekunde
- Rate-Limit Handling: Respektiert `Retry-After` Header

## Advanced Features

### Verfügbarkeitsprüfung

```python
from calendly_client import CalendlyClient

async with CalendlyClient() as client:
    # Prüfe Verfügbarkeit
    is_available = await client.check_slot_availability(
        event_type_uri="https://api.calendly.com/event_types/...",
        date="2024-03-15",
        time="14:00",
        timezone="Europe/Berlin"
    )

    # Verfügbare Slots abrufen
    slots = await client.get_available_slots(
        event_type_uri="...",
        start_date="2024-03-15",
        end_date="2024-03-20"
    )
```

### Custom Questions

```python
result = await client.book_appointment(
    name="Test User",
    email="test@example.com",
    date="2024-03-15",
    time="14:00",
    custom_questions={
        "Lead Source": "Voice Agent",
        "Interesse": "KI-Automatisierung",
        "Unternehmensgröße": "50-200 Mitarbeiter"
    }
)
```

### Scheduling Links

```python
# Erstelle einen generischen Booking-Link
link = await client.create_scheduling_link(
    event_type_uri="https://api.calendly.com/event_types/...",
    max_event_count=1
)
```

## Monitoring

### Supabase Integration

Alle Buchungen werden in Supabase gespeichert:

**Tabelle**: `appointments`

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| conversation_id | UUID | Vapi Call ID |
| phone_number | string | Anrufer-Nummer |
| name | string | Name des Teilnehmers |
| email | string | E-Mail-Adresse |
| appointment_date | date | Termindatum |
| appointment_time | time | Terminzeit |
| company | string | Firmenname |
| notes | text | Gesprächsnotizen |
| booking_status | string | confirmed/error |
| success | boolean | Buchung erfolgreich |
| calendly_event_uri | string | Calendly Event URI |
| calendly_invitee_uri | string | Invitee URI |
| error_message | text | Fehlermeldung (falls vorhanden) |
| created_at | timestamp | Zeitstempel |

### Dashboard Metriken

Die API bietet Endpunkte für Dashboard-Statistiken:

```bash
# Konversionsrate
GET /api/stats/conversion

# Lead-Score-Verteilung
GET /api/stats/lead-scores

# Kürzliche Anrufe
GET /api/stats/recent-calls
```

## Troubleshooting

### API Token funktioniert nicht

1. Überprüfen Sie Token-Gültigkeit:
   ```bash
   curl -X GET https://api.calendly.com/users/me \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. Prüfen Sie Calendly Plan:
   - API-Zugriff erfordert Professional Plan oder höher
   - Basic-Plan hat keinen API-Zugriff

### Termine werden nicht gebucht

1. Prüfen Sie Event Type URI:
   ```bash
   curl -X GET "https://api.calendly.com/event_types?user=YOUR_USER_URI" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. Prüfen Sie Verfügbarkeit:
   ```bash
   curl -X GET "https://api.calendly.com/event_type_available_times?event_type=YOUR_EVENT_TYPE&start_time=2024-03-15T00:00:00&end_time=2024-03-15T23:59:59" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### Zeitzone Probleme

- Standard: `Europe/Berlin`
- Calendly speichert in UTC, konvertiert automatisch
- Überprüfen Sie Timezone-Parameter im Webhook

### SSL/TLS Fehler

Bei Selbstzertifikaten oder Proxy-Problemen:
```python
# Deaktiviere SSL-Verification (nur für Entwicklung)
client = httpx.AsyncClient(verify=False)
```

## Best Practices

### 1. API Token Security
- Speichern Sie Token in `.env` Datei
- Nie im Code hardcoden
- Rotieren Sie Token regelmäßig

### 2. Error Handling
- Implementieren Sie Fallback-Verhalten
- Loggen Sie Fehler für Debugging
- Zeigen Sie benutzerfreundliche Nachrichten

### 3. Rate Limiting
- Calendly erlaubt 200 requests/minute
- Client implementiert automatische Delays
- Überwachen Sie 429 Responses

### 4. Testing
- Verwenden Sie Test-Event-Types
- Löschen Sie Test-Buchungen nach Tests
- Nutzen Sie dedizierte Test-Accounts

## Support

### Ressourcen
- [Calendly API Docs](https://developer.calendly.com/)
- [API Rate Limits](https://developer.calendly.com/rate-limits)
- [Error Codes](https://developer.calendly.com/errors)

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration

### Von Legacy-Implementation

Die neue Implementation ist rückwärtskompatibel. Die Legacy-Funktion `_book_calendly_legacy` wird als Fallback verwendet, falls der neue Client nicht verfügbar ist.

### Database Schema

Führen Sie folgendes SQL aus, um die `appointments`-Tabelle zu aktualisieren:

```sql
-- Neue Spalten hinzufügen
ALTER TABLE appointments
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
ADD COLUMN IF NOT EXISTS calendly_event_uri TEXT,
ADD COLUMN IF NOT EXISTS calendly_invitee_uri TEXT,
ADD COLUMN IF NOT EXISTS confirmation_url TEXT,
ADD COLUMN IF NOT EXISTS error_code VARCHAR(50),
ADD COLUMN IF NOT EXISTS success BOOLEAN DEFAULT FALSE;
```
