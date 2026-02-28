# Everlast Dashboard Design System v2.0

## Design Philosophy
- **Linear-inspired**: Clean, minimal, purposeful
- **Vercel-inspired**: Developer-first, high contrast
- **Notion-inspired**: Content-focused, spacious

## Color Palette

### Light Mode
| Token | Value | Usage |
|-------|-------|-------|
| --bg-primary | #ffffff | Main background |
| --bg-secondary | #f8fafc | Cards, sections |
| --bg-tertiary | #f1f5f9 | Hover states |
| --border | #e2e8f0 | Borders, dividers |
| --text-primary | #0f172a | Headings |
| --text-secondary | #475569 | Body text |
| --text-tertiary | #94a3b8 | Muted text |

### Dark Mode
| Token | Value | Usage |
|-------|-------|-------|
| --bg-primary | #0a0a0a | Main background |
| --bg-secondary | #141414 | Cards |
| --bg-tertiary | #1a1a1a | Hover states |
| --border | #262626 | Borders |
| --text-primary | #fafafa | Headings |
| --text-secondary | #a1a1a1 | Body text |

### Brand Colors
| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| accent | #0ea5e9 | #38bdf8 | Primary actions |
| success | #22c55e | #4ade80 | Success states |
| warning | #f59e0b | #fbbf24 | Warnings |
| danger | #ef4444 | #f87171 | Errors |
| lead-a | #22c55e | #4ade80 | Hot leads |
| lead-b | #3b82f6 | #60a5fa | Warm leads |
| lead-c | #f59e0b | #fbbf24 | Cold leads |
| lead-n | #6b7280 | #9ca3af | No leads |

## Typography
- **Font**: Geist Sans (Primary), Inter (Fallback)
- **Scale**:
  - H1: 2rem (32px), font-weight: 700
  - H2: 1.5rem (24px), font-weight: 600
  - H3: 1.25rem (20px), font-weight: 600
  - Body: 0.875rem (14px), font-weight: 400
  - Small: 0.75rem (12px), font-weight: 400

## Spacing Scale
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

## Border Radius
- sm: 0.375rem (6px)
- md: 0.5rem (8px)
- lg: 0.75rem (12px)
- xl: 1rem (16px)
- 2xl: 1.5rem (24px)
- full: 9999px

## Shadows
- sm: 0 1px 2px rgba(0,0,0,0.05)
- md: 0 4px 6px rgba(0,0,0,0.07)
- lg: 0 10px 15px rgba(0,0,0,0.1)
- glow: 0 0 20px rgba(14,165,233,0.3)

## Animation Durations
- fast: 150ms
- normal: 300ms
- slow: 500ms

## Easing Functions
- default: cubic-bezier(0.4, 0, 0.2, 1)
- bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)
- smooth: cubic-bezier(0.25, 0.1, 0.25, 1)
