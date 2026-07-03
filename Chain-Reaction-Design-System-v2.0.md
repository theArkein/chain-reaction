# Chain Reaction — Design System (v2.0)

**Status:** Current. Describes the shipped app (`index.html`).
**Last updated:** 2026-07-03
**Companion spec:** `Chain-Reaction-Gameplay-PRD-v1.2.md` (game logic — the source of truth for all state this UI renders).

> **Maintenance rule.** This is a living document. Every UI/UX change ships **with** a matching update here — tokens, components, motion, sound, or copy — and a new changelog row. This doc owns *appearance and interaction*; the PRD owns *behavior*.

---

## 1. Design principles

- **Low-chrome and type-led.** Borderless grouping with hairline separators, ghost controls, generous whitespace. Boxes and heavy fills are avoided; hierarchy comes from type weight and spacing.
- **The board is the hero.** Everything else is quiet so the grid and its chain reactions dominate.
- **Two config layers, never mixed.** *Match setup* (mode, board, players, format) is chosen before a game and locked during play. *Preferences* (sound, haptics, animation, theme) are global and changeable anytime. They live in different places (see §4).
- **Color means player.** The interface is neutral; the only saturated colors are the (up to four) players. Color always denotes ownership.
- **State legible at a glance.** Each game-state field maps to exactly one visual channel (§8).
- **Motion clarifies, never decorates.** Animation makes cascades readable and confirms input; it is brisk and can be reduced or switched off.
- **Mobile-first and robust.** Designed for a phone in portrait; hardened against zoom, overscroll, and selection (§9).

---

## 2. Foundations

### 2.1 Color tokens

CSS custom properties. Player colors are constant across themes; everything else flips with `data-theme`.

**Players (constant)**

| Token | Value | Role |
|---|---|---|
| `--p1` / `--p1-soft` | `#4C86F0` / `rgba(76,134,240,.14)` | Player 1 — blue |
| `--p2` / `--p2-soft` | `#F35B54` / `rgba(243,91,84,.14)` | Player 2 / Bot — coral |
| `--p3` / `--p3-soft` | `#46B36B` / `rgba(70,179,107,.14)` | Player 3 — green |
| `--p4` / `--p4-soft` | `#E0A32E` / `rgba(224,163,46,.14)` | Player 4 — amber |

The `-soft` tints are used for the active player's cell background.

**Light theme**

| Token | Value |
|---|---|
| `--bg` | `#FAFAF8` |
| `--surface` | `#FFFFFF` |
| `--surface-2` | `#F1F1EE` (control tracks, hover) |
| `--tile` | `#ECEBE7` (empty board cell) |
| `--text` | `#161618` (also the primary-button fill) |
| `--dim` | `#9C9CA2` (secondary/label text) |
| `--border` | `rgba(0,0,0,.055)` (hairlines) |
| `--shadow` | `0 20px 60px rgba(0,0,0,.14)` |

**Dark theme**

| Token | Value |
|---|---|
| `--bg` | `#0D0D0F` |
| `--surface` | `#161619` |
| `--surface-2` | `#1E1E22` |
| `--tile` | `#212127` |
| `--text` | `#F5F5F6` |
| `--dim` | `#7E7E86` |
| `--border` | `rgba(255,255,255,.07)` |
| `--shadow` | `0 20px 60px rgba(0,0,0,.6)` |

### 2.2 Typography

- **Family:** `Inter`, → `Segoe UI`, `system-ui`, `-apple-system`, sans-serif, with `-webkit-font-smoothing:antialiased`.
- **Weights:** 600 (labels/controls), 700 (values, buttons, turn text), 800 (titles, headings, verdict).
- **Scale (approx):** win heading 30px/800; brand 18px/800; option label 15px/600; seg/stat 13–15px; verdict 11px/800 with 3px tracking, uppercase.
- **Numerals:** `font-variant-numeric: tabular-nums` on counts, stepper value, and stats so digits don't jitter.
- **Case:** sentence case everywhere except the verdict micro-label (uppercase).

### 2.3 Space, shape, elevation

- **Radius:** `--radius: 18px` (cells); 14–16px buttons; 12px seg tracks; 26px top corners on the preferences sheet; 999px pills (chips, toast); 50% for orbs, pips, logo dots, icon buttons, stepper buttons.
- **App width:** screens centered, `max-width: 432px` (app-like column).
- **Board gap / cell radius scale with size** `S`: gap 11→4px and radius 16→6px as `S` goes 4→12, so large boards stay clean.
- **Elevation:** near-flat. `--shadow` is reserved for genuinely floating layers (preferences sheet, win overlay, toast) and the primary Play button's presence. Hairlines (`--border`) do the separating elsewhere.

### 2.4 Motion

Shared easing `--ease: cubic-bezier(.32,.72,0,1)`. Scaled by the Animation setting (Full ×1, Reduced ×0.6, Off = skipped).

| Animation | Where | Spec |
|---|---|---|
| `fade` | screen/overlay/toast enter | 0.3–0.4s, opacity + 8px rise |
| `pop` | orb first appears | 0.18s scale 0.5→1 |
| `bump` | placing an orb on your move | 0.18s scale 1→1.12→1 |
| `boom` | a cell exploding | 0.20s scale 1→1.3→0.1, fade |
| particle fly | orbs travelling to neighbors in a wave | 0.17s translate |
| ratio bar | board-control width change | 0.45s width |
| `slideup` | preferences bottom sheet | 0.3s translateY(100%)→0 |

Per-wave cascade rhythm (Full): burst ~140ms → fly ~175ms → settle ~65ms. Off applies deposits instantly with no particles.

---

## 3. Theming

`data-theme="light" | "dark"` on `<body>` flips all themed tokens (default light). A moon icon on the home screen toggles it; it's also in Preferences. `<meta name="theme-color">` is set per scheme so the mobile browser chrome matches.

---

## 4. Information architecture (two layers)

- **Home = match configurator.** A `Friends | Bot` mode toggle at the top; below it, only the options relevant to the mode appear — board size (both), Players + Format (Friends), Difficulty (Bot) — then a single **Play** button. A gear (top-right) opens Preferences. The two option blocks share one grid cell so switching modes causes **no layout shift** (the inactive block is `visibility:hidden`, keeping its height).
- **Preferences = global, contextual.** A bottom sheet holding Sound, Haptics, Animation, Theme — reachable from home and during a game. **Bot difficulty appears here only during a bot game** (live-adjustable, with a toast); pre-game it lives on the home screen.
- **During play, match setup is absent.** The game screen shows only back-to-home and the gear, so board/players/format can't change mid-game. Reconfiguring means returning home.

---

## 5. Components

### 5.1 Home configurator
- **Brand:** two overlapping color dots (P1, P2) + wordmark, 18px/800.
- **Mode toggle** (`.seg.full.modeseg`): prominent two-option segmented control; the active option is a raised `--surface` pill.
- **Option rows** (`.row`): hairline-separated, label left, control right. `Players` and `Format` are `friends`-tagged; `Format`'s Teams option is disabled unless Players = 4.
- **Board-size stepper:** round ghost `−`/`+` buttons flanking an `N×N` value (tabular), clamped 4–12.
- **Play button:** full-width, `--text` fill, 16px radius — the one primary action.

### 5.2 Game header & score
- **Header** (`.gbar`): ghost back-to-home (chevron), centered turn text with a colored dot, ghost gear. Icon buttons are borderless with a circular hover.
- **2-player score** (`.ctrl`): `[dot + count]  [ratio bar]  [count + dot]`. The ratio bar is a `--tile` track split by occupied-cell share (P1 from left, P2 from right), animated.
- **3–4 player score** (`.hud`): a row of rounded **chips**, one per player (colored dot + `P# · count`), with a team tag in 2v2; the current player's chip gets a `--text` ring, eliminated players are dimmed + struck through. (Ratio bar shows for 2 players; chips for 3–4.)

### 5.3 Cell, orb, pips
- **Cell:** `--tile` rounded square; the active player's owned cells tint to `--pX-soft`; clickable cells get a pointer and `scale(1.04)` hover.
- **Orb:** 74%-of-cell circle in the owner color. Count 1–3 shown as white **pips** (1 centered · 2 diagonal · 3 triangular). The UI never draws a stable 4 (clamp-at-4 + explosion).
- **Particles:** during a wave, orb-colored dots (30% of cell) fly from the exploding cell to each neighbor, then vanish as the deposit lands — the primary "what's happening" cue.

### 5.4 Preferences sheet
Bottom sheet (`.modal` bottom-aligned, `.sheet` slides up, rounded top, safe-area bottom padding). Rows: Sound/Haptics **toggles**; Animation/Theme **segmented**; **Bot difficulty** (full-width 5-option segmented) shown only during a bot game. Tapping the scrim or Done closes it.

### 5.5 End overlay
Blurred scrim over the board: a colored crown badge, the result heading in the winner's color ("You win!" / "Bot wins" / "Player N wins" / "Team A/B wins"), a **verdict** micro-label (Domination / Nail-biter / Comeback / Clean sweep / Hard-fought), a stats card, a dim footer (duration · turns · board size), and Home / Rematch buttons. 2-player games show verdict + winning chain + comeback-or-biggest-chain + lead changes; 3–4 players show a simpler chain/format summary.

### 5.6 Toast
Bottom-center pill (`--text` on `--bg`), slides up, auto-dismisses ~1.7s. Used to confirm a live bot-difficulty change mid-game.

---

## 6. Controls reference

- **Segmented (`.seg`)** — `--surface-2` track, active button is a raised `--surface` pill; `.full` variant stretches buttons to equal width; disabled options are dimmed.
- **Toggle (`.toggle`)** — 46×28 track, sliding white knob; ON = `--p1` (blue) track.
- **Icon button (`.icon-btn`)** — borderless ghost, 40px circle, `--dim`→`--text` on hover, `aria-label` required.
- **Buttons (`.btn`)** — hairline secondary; `.primary` = `--text` fill; `.wide` = full width.

---

## 7. Players & teams

Up to four players use the four fixed colors (blue, coral, green, amber). In **2v2 teams**, teammates keep distinct colors (so each player can identify their own cells) and are grouped by a team tag in the HUD; the win is decided per team. The bot is always Player 2 (coral) in bot mode.

---

## 8. State → visual mapping (source of truth)

| Game state (PRD) | Visual channel |
|---|---|
| `owner` (NONE / P1–P4) | orb color (none / blue / coral / green / amber) |
| `count` (0–3 stable) | pip count on the orb |
| active player (turn) | cell tint + turn-text dot + current chip ring |
| occupied-cell totals | ratio bar (2p) or per-player chips (3–4p) |
| explosion (`count 4`, transient) | `boom` + flying particles; never a static tile |
| elimination (0 cells) | chip dimmed + struck through |
| game over / winner | end overlay (crown, heading, verdict, stats) |

Any new game state gets a row here and a defined channel **before** it ships.

---

## 9. Mobile & cross-platform

- **Viewport locked:** `user-scalable=no`, `maximum/minimum-scale=1`, `viewport-fit=cover`.
- **No zoom:** global `touch-action: manipulation` (kills double-tap zoom and tap delay); iOS pinch `gesture*` events `preventDefault`ed in JS.
- **No rubber-band / pull-to-refresh:** `overscroll-behavior:none` on `html`/`body`; layout fits the viewport.
- **No selection / callouts:** `user-select:none`, `-webkit-touch-callout:none`, `contextmenu` suppressed.
- **Sizing:** `100dvh` (dynamic viewport) with `100vh` fallback; `overflow-x:hidden`.
- **Safe areas:** `env(safe-area-inset-*)` padding around all screens (min 18–20px) and on the preferences sheet bottom.
- **PWA meta:** `theme-color` per scheme and `apple-mobile-web-app-*` for home-screen launches.

---

## 10. Accessibility

- **Don't rely on hue alone.** Ownership is reinforced by the active-turn tint, turn text, chip ring, and score; count is always a non-color channel (pips). Preserve one non-color cue per state when adding skins.
- **Reduced / Off motion** is a first-class setting; honor it for any new animation.
- **Targets:** cells scale with the board; controls are ≥32–40px. Keep clickable cells comfortably tappable at the 12×12 max.
- **Contrast:** verify `--text`/`--dim` and white pips on orbs against WCAG in both themes when tuning colors.
- **Icon buttons** keep `aria-label`s.
- **Future:** a colour-blind option (shape/texture per player) and auto-honoring `prefers-reduced-motion`.

---

## 11. Open items

- Persist settings/config across sessions (currently in-memory; resets on reload).
- Colour-blind-friendly skin (per-player shape/texture).
- Auto-map `prefers-reduced-motion` to Animation = Reduced/Off.
- Localizable copy pass.

---

## 12. Changelog

| Version | Date | Change |
|---|---|---|
| v2.0 | 2026-07-03 | Rewrite for the current app: two-layer IA (adaptive home configurator + contextual bottom-sheet Preferences); fresh low-chrome "sleek v2" visual system (new palette, hairline layout, ghost controls, board-hero, tabular numerals); four player colors + 2v2 team HUD chips; board-size stepper (4–12); mode-toggle layout-shift fix; motion catalogue; mobile-hardening section. Supersedes v1.0/v0.1. |
| v1.0 | 2026-07-03 | Sleek-minimal system for the 2-player + bot app (retired). |
| v0.1 | 2026-07-03 | Base system captured from the original reference board (retired). |

*(Add a row for every UI/UX change; bump the version and "Last updated".)*
