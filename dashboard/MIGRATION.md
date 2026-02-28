# Dashboard V2 - Migration Guide

## Übersicht
Das Dashboard wurde komplett überarbeitet mit einem Premium Design (Linear/Vercel inspiriert), Dark Mode Support, Animationen und verbesserten Charts.

## Neue Features

### 🎨 Design
- **Premium UI**: Linear/Vercel/Notion inspiriert
- **Dark Mode**: Vollständiger Support mit `class` Strategy
- **Animationen**: Framer Motion für sanfte Übergänge
- **Glassmorphism**: Moderne Card-Designs mit Blur-Effekten
- **Responsive**: Mobile-first Approach

### 📊 Datenvisualisierung
- **Call Volume Timeline**: Area Chart mit Gradienten
- **Lead Distribution**: Interaktiver Pie Chart
- **Objection Analysis**: Bar Chart mit Outcomes
- **Custom Tooltips**: Premium Styled Tooltips

### ⚡ Performance
- **Skeleton Loading**: Statt einfacher Spinner
- **Empty States**: Schöne UI wenn keine Daten
- **Animations**: Staggered Animations für Content
- **Real-time**: Supabase Subscriptions

## Installation

### 1. Dependencies installieren
```bash
cd dashboard
npm install framer-motion tailwind-merge
```

### 2. Tailwind Config prüfen
`tailwind.config.ts` sollte `darkMode: 'class'` enthalten:

```typescript
const config: Config = {
  darkMode: 'class',
  // ... rest
}
```

### 3. Umgebungsvariablen
Stelle sicher, dass diese gesetzt sind:
```env
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## Dateien

### Neue Dateien
- `components/DashboardV2.tsx` - Hauptkomponente
- `components/ui/Button.tsx` - Button Komponente
- `components/ui/Card.tsx` - Card mit Varianten
- `components/ui/Badge.tsx` - Badge Komponente
- `components/ui/Skeleton.tsx` - Skeleton Loading
- `hooks/useTheme.ts` - Theme Management
- `hooks/useRealtimeData.ts` - Realtime Data Hook
- `lib/utils.ts` - Utility Funktionen
- `design-system.md` - Design Dokumentation

### Geänderte Dateien
- `app/page.tsx` - Verwendet jetzt DashboardV2
- `package.json` - Neue Dependencies
- `tailwind.config.ts` - Dark Mode aktiviert

## Design System

### Farbpalette

#### Light Mode
- Background: `#ffffff` / `#f8fafc`
- Text Primary: `#0f172a`
- Text Secondary: `#475569`
- Border: `#e2e8f0`

#### Dark Mode
- Background: `#0a0a0a` / `#141414`
- Text Primary: `#fafafa`
- Text Secondary: `#a1a1aa`
- Border: `#262626`

### Brand Colors
- Accent: `#0ea5e9` (Light) / `#38bdf8` (Dark)
- Success: `#22c55e`
- Warning: `#f59e0b`
- Danger: `#ef4444`

## Komponenten

### Card Variants
- `default`: Standard weiß/grau Card
- `glass`: Glassmorphism mit Blur
- `elevated`: Mit Schatten

### Button Variants
- `primary`: Sky Blue Action
- `secondary`: Grauer Button
- `ghost`: Transparent mit Hover
- `danger`: Roter Button

## Hooks

### useTheme
```typescript
const { theme, setTheme, resolvedTheme } = useTheme()
// theme: 'light' | 'dark' | 'system'
// setTheme('dark') | setTheme('light')
```

### useRealtimeData
```typescript
const { data, loading, error, refetch } = useRealtimeData({
  supabase,
  table: 'calls',
  select: '*',
  orderBy: { column: 'created_at', ascending: false },
  limit: 10,
})
```

## Charts

### Area Chart (Call Volume)
- Zeigt Calls und Appointments über Zeit
- Gradienten für moderne Optik
- Custom Tooltip

### Pie Chart (Lead Distribution)
- A/B/C/N Lead Scores
- Interaktive Slices
- Legend

### Bar Chart (Objections)
- Einwände nach Typ
- Outcome Statistiken
- Responsive

## Animationen

### Container Stagger
```typescript
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}
```

### Item Fade Up
```typescript
const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
}
```

## Rollback

Falls nötig, kannst du zum alten Dashboard zurück:

1. `app/page.tsx` ändern:
```typescript
import Dashboard from '@/components/Dashboard'
export default function Home() {
  return <Dashboard />
}
```

2. DashboardV2 Komponenten löschen (optional)

## Troubleshooting

### Dark Mode funktioniert nicht
- Prüfe `darkMode: 'class'` in tailwind.config.ts
- Stelle sicher dass `resolvedTheme` verwendet wird

### Animationen zu schnell/langsam
- Passe `duration` in den variants an
- Standard: 0.5s für items, 0.3s für hover

### Charts nicht sichtbar
- Stelle sicher dass Container eine feste Höhe hat
- Prüfe dass Recharts installiert ist

## Nächste Schritte

1. [ ] Echte Daten testen
2. [ ] Mobile Responsiveness testen
3. [ ] Dark Mode Toggle testen
4. [ ] Animationen bei langsamer Verbindung testen
5. [ ] Performance Audit (Lighthouse)

## Support

Bei Fragen:
- Design System: `design-system.md`
- Component API: Siehe Komponenten-Dateien
- TypeScript: Alle Komponenten sind typed
