# EVERLAST VOICE AGENT - DEPLOYMENT GUIDE

## 🚀 Schnellstart (Copy & Paste)

### Voraussetzungen

Stellen Sie sicher, dass folgende Tools installiert sind:
- Node.js 20+
- Python 3.11+
- Railway CLI: `npm install -g @railway/cli`
- Vercel CLI: `npm install -g vercel`
- Supabase CLI: `npm install -g supabase`

### Environment Variables

Erstellen Sie eine `.env` Datei im Root:

```env
# Vapi
VAPI_API_KEY=sk_your_vapi_key

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...

# Calendly
CALENDLY_API_KEY=eyJ...
CALENDLY_USER_URI=https://api.calendly.com/users/...
CALENDLY_EVENT_TYPE_URI=https://api.calendly.com/event_types/...

# Optional
ELEVENLABS_API_KEY=sk_...
```

---

## 1️⃣ SUPABASE (Datenbank)

```bash
# Login
supabase login

# Projekt verlinken
supabase link --project-ref YOUR_PROJECT_REF

# Schema pushen
supabase db push

# Oder SQL manuell ausführen
supabase sql < supabase/schema.sql
supabase sql < supabase/rls_policies.sql
supabase sql < supabase/checkpoints.sql
```

---

## 2️⃣ RAILWAY (Backend)

```bash
cd api

# Login
railway login

# Projekt erstellen (falls nicht existiert)
railway init --name everlast-voice-agent

# Oder zu bestehendem Projekt verlinken
railway link

# Environment Variables setzen
railway variables set VAPI_API_KEY="$VAPI_API_KEY"
railway variables set SUPABASE_URL="$SUPABASE_URL"
railway variables set SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
railway variables set CALENDLY_API_KEY="$CALENDLY_API_KEY"
railway variables set CALENDLY_USER_URI="$CALENDLY_USER_URI"
railway variables set CALENDLY_EVENT_TYPE_URI="$CALENDLY_EVENT_TYPE_URI"
railway variables set ENVIRONMENT="production"
railway variables set CHECKPOINTER_BACKEND="supabase"

# Deploy
railway up

# Domain abrufen
railway domain
```

**Ausgabe:** `https://everlast-voice-agent.up.railway.app`

---

## 3️⃣ VERCEL (Dashboard)

```bash
cd dashboard

# Login
vercel login

# Projekt verlinken
vercel link --project everlast-dashboard

# Environment Variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Eingabe: Ihre Supabase URL

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Eingabe: Ihr Supabase Anon Key

# Deploy
vercel --prod
```

**Ausgabe:** `https://everlast-dashboard.vercel.app`

---

## 4️⃣ VAPI (Voice Agent)

```bash
# Assistant JSON aktualisieren mit Backend URL
sed -i "s|https://everlast-api.railway.app|YOUR_RAILWAY_URL|g" vapi/assistant.json

# Assistant importieren
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @vapi/assistant.json

# Workflow importieren (optional)
curl -X POST https://api.vapi.ai/workflow \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @vapi/workflow.json
```

---

## 5️⃣ KONFIGURATION

### Webhook URL konfigurieren

In Vapi Dashboard:
1. Assistant öffnen
2. Server URL setzen: `https://YOUR_RAILWAY_URL/vapi/webhook`
3. Secret setzen: `VAPI_SERVER_SECRET` aus .env

### Telefonnummer kaufen

1. Vapi Dashboard → Phone Numbers
2. Deutsche Nummer kaufen
3. Mit Assistant verlinken

### Calendly verbinden

1. Calendly Developer Console
2. Event Type erstellen
3. URI kopieren und in Railway ENV setzen

---

## ✅ VERIFIKATION

### Backend testen

```bash
curl https://YOUR_RAILWAY_URL/health
```

**Erwartete Ausgabe:**
```json
{
  "status": "healthy",
  "supabase_connected": true,
  "timestamp": "2026-02-26T..."
}
```

### Dashboard testen

Öffnen Sie: `https://everlast-dashboard.vercel.app`

### Voice Agent testen

1. Deutsche Vapi-Nummer anrufen
2. Mit "Anna" sprechen
3. Dashboard prüfen

---

## 🔧 TROUBLESHOOTING

### Railway Deployment fehlschlägt

```bash
# Logs prüfen
railway logs

# Rebuild
railway up --detach
```

### Supabase Connection failed

```bash
# Connection testen
supabase status

# RLS Policies prüfen
supabase sql "SELECT * FROM pg_policies WHERE schemaname = 'public';"
```

### Vapi Webhook nicht erreichbar

```bash
# Webhook testen
curl -X POST https://YOUR_RAILWAY_URL/vapi/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","content":"Test"}}'
```

---

## 📊 POST-DEPLOYMENT

### Monitoring einrichten

1. **Railway:** Dashboard → Metrics
2. **Supabase:** Database → Logs
3. **Vercel:** Dashboard → Analytics

### Backups

```bash
# Supabase Backup
supabase db dump -f backup.sql
```

### Updates

```bash
# Backend updaten
cd api
git pull
railway up

# Dashboard updaten
cd dashboard
git pull
vercel --prod
```

---

## 🎯 DEPLOYMENT CHECKLIST

- [ ] Environment Variables gesetzt
- [ ] Supabase Schema gepusht
- [ ] Railway deployed
- [ ] Vercel deployed
- [ ] Vapi Assistant importiert
- [ ] Webhook URL konfiguriert
- [ ] Telefonnummer gekauft
- [ ] Calendly verbunden
- [ ] Test-Call durchgeführt
- [ ] Dashboard funktioniert

---

**Fertig!** 🎉
