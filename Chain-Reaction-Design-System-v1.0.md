# Chain Reaction — Design System (v1.0)

**Status:** Current. Describes the shipped sleek-minimal app (`chain-reaction.html`).
**Last updated:** 2026-07-03
**Companion spec:** `Chain-Reaction-Gameplay-PRD-v1.1.md` (game logic — the source of truth for all state this UI renders).

> **Maintenance rule.** This is a living document. Every UI/UX change ships **with** a matching update here — tokens, components, motion, sound, or copy — and a new changelog row. If the app and this doc disagree, one of them is wrong. This doc owns *appearance and interaction*; the PRD owns *behavior*.

---

## 1. Design principles

- **Sleek minimal.** Flat surfaces, hairline borders, soft shadows only for lift. No gradients, no skeuomorphism. Whitespace does the work.
- **Two colors carry meaning.** The interface is neutral greys; the only saturated colors are the two players (blue / coral). Color is never decorative — it always means "player 1" or "player 2."
- **State legible at a glance.** Each piece of game state has exactly one visual channel (see §8). A player reads ownership, orb count, whose turn it is, and who's ahead without stopping to think.
- **Motion clarifies, never decorates.** Animation exists to make the cascade readable and to confirm input — it is brisk and can be reduced or switched off.
- **One device, calm surface.** Designed for a single phone or desktop window; content is centered with a max width and adapts down.

---

## 2. Foundations

### 2.1 Color tokens

Defined as CSS custom properties; all themed values flip with `data-theme`. Player colors are constant across themes.

**Constant (both themes)**

| Token | Value | Role |
|---|---|---|
| `--p1` | `#4C86F0` | Player 1 (blue) — orbs, accents, "you" |
| `--p1-soft` | `rgba(76,134,240,.16)` | Player 1 active-cell tint |
| `--p2` | `#F35B54` | Player 2 / Bot (coral) |
| `--p2-soft` | `rgba(243,91,84,.16)` | Player 2 active-cell tint |

**Light theme**

| Token | Value | Role |
|---|---|---|
| `--bg` | `#F4F4F2` | Page background |
| `--surface` | `#FFFFFF` | Cards, buttons, pills |
| `--surface-2` | `#FBFBFA` | Secondary hover surface |
| `--tile` | `#E7E6E2` | Empty board cell, control tracks |
| `--text` | `#1B1B1D` | Primary text; also the "primary button" fill |
| `--dim` | `#6B6B72` | Secondary/label text |
| `--border` | `rgba(0,0,0,.09)` | Hairline borders |
| `--shadow` | `0 10px 40px rgba(0,0,0,.10)` | Card/lift shadow |

**Dark theme**

| Token | Value |
|---|---|
| `--bg` | `#131315` |
| `--surface` | `#1E1E22` |
| `--surface-2` | `#26262B` |
| `--tile` | `#2B2B31` |
| `--text` | `#F1F1F3` |
| `--dim` | `#9A9AA3` |
| `--border` | `rgba(255,255,255,.10)` |
| `--shadow` | `0 10px 40px rgba(0,0,0,.45)` |

### 2.2 Typography

- **Family:** `Inter`, falling back to `Segoe UI`, `system-ui`, `-apple-system`, sans-serif.
- **Weights:** 600 (default UI), 700 (stat values, toast), 800 (titles, buttons, headings). Regular 400 for body/labels.
- **Scale (approx):** title 40px/800 (menu H1), screen heading 30px/800 (win), stat value 15–16px/700, label 15px/600, caption 12–13px, verdict 12px/800 with 2.5px letter-spacing uppercase.
- **Case:** sentence case everywhere except the verdict word (intentional uppercase micro-label).

### 2.3 Space, shape, elevation

- **Radius:** `--radius: 16px` (cells, menu buttons); 12px for icon buttons, pills, chips; 20px for modal sheets and overlay; 50% for orbs/pips/logo dots.
- **Board gap:** 11px between cells; grid is `aspect-ratio:1/1`, 5 equal columns.
- **Container:** screens are centered, `max-width:520px` (settings sheet 400px).
- **Elevation:** flat by default; `--shadow` used sparingly for menu buttons, chips, modal, toast. No inner shadows or borders-plus-shadow stacking.

### 2.4 Motion

Shared easing token `--ease: cubic-bezier(.4,0,.2,1)`. All durations are short; the whole set is scaled by the Animation setting (Full ×1, Reduced ×0.6, Off = skipped).

| Animation | Where | Spec |
|---|---|---|
| `fade` | screen enter, overlay/toast show | 0.25–0.35s, opacity + 6px rise |
| `pop` | orb first appears | 0.16s scale 0.55→1 |
| `bump` | placing an orb on your move | 0.16s scale 1→1.12→1 |
| `boom` | a cell exploding | 0.20s scale 1→1.28→0.12, fade out |
| particle fly | orbs travelling to neighbors during a cascade wave | 0.17s translate, `--ease` |
| ratio bar | board-control bar width change | 0.40s width |
| tile tint | active-player highlight | 0.20s background |

Per-wave cascade rhythm (Full speed): burst ~140ms → fly ~175ms → settle ~65ms. Reduced ×0.6; Off applies deposits instantly with no particles.

---

## 3. Theming

`data-theme="light" | "dark"` on `<body>` switches all themed tokens. Toggle is available on the menu (moon icon) and in Settings. Default: light. Theme changes apply live everywhere via CSS variable cascade.

---

## 4. Components

### 4.1 Screens

Three top-level screens (`.screen`, one `.active` at a time) plus two floating layers.

- **Menu** — logo (two color dots), title, tagline, two primary actions ("Play with a friend", "Play against the bot"), and a footer with Settings + theme toggle.
- **Game** — header bar, control/ratio bar, board, and the end overlay (child of this screen).
- **Settings** — modal sheet over a scrim.
- **Toast** — transient bottom-center pill (see §4.9).
- **End overlay** — blurred scrim over the board (see §4.8).

### 4.2 Buttons

- **Primary button** (`.menu-btn.primary`, `.btn.primary`): fill `--text`, label `--bg`. One per view max — the main action.
- **Secondary button** (`.menu-btn`, `.btn`): `--surface` fill, `--border` hairline, hover lift/`--surface-2`.
- **Icon button** (`.icon-btn`): 42px square, 12px radius, hairline border, 20px stroked SVG (1.5–2px), `aria-label` required. Used for back, settings gear, theme.
- Active state: `scale(.97–.94)`.

### 4.3 Turn pill

Full-width pill in the game header. Shows a colored `.tdot` in the current player's color plus text: "Your turn" (vs bot), "Bot is thinking…", or "Player N · your turn" (hotseat). Background transitions on turn change.

### 4.4 Control / ratio bar

Below the header: `[dot + P1 cell count]  [ratio bar]  [P2 cell count + dot]`. The ratio bar is a rounded `--tile` track split into a coral segment (left, P1 share) and blue segment (right, P2 share), widths proportional to each player's occupied-cell share, animated (0.4s). Updates at the end of every turn.

### 4.5 Cell

Board unit: a `--tile` rounded square with an optional orb.

| State | Trigger (PRD field) | Appearance |
|---|---|---|
| Empty | `count 0`, `owner NONE` | plain `--tile` |
| Owned (inactive) | `count>0`, not current player | orb + pips, plain tile |
| Owned (active) | `count>0`, owner = current player | orb + pips, tile tinted `--pX-soft` |
| Clickable | legal move for the human this turn | pointer + hover `scale(1.03)` |
| Exploding | `count 4` mid-cascade | `boom` animation, then cleared |

The active tint marks exactly the legal-move set (PRD §5.2) and only shows for a human's turn — the bot's cells are never rendered clickable.

### 4.6 Orb & pips

An orb is a 72%-of-cell circle in the owner color. Orb count (PRD `count`, 1–3 stable) is shown as white pips: 1 centered · 2 diagonal · 3 triangular. The UI never draws a stable "4" (clamp-at-4 + explosion; PRD §6.1.3).

### 4.7 Particles

During each cascade wave, small orb-colored circles (30% of cell size) animate from the exploding cell's center to each orthogonal neighbor, then are removed as the deposit lands. This is the primary "what's happening" cue for chains. Skipped when Animation = Off.

### 4.8 End overlay

Blurred scrim over the board. Contents, top to bottom: a colored crown badge, the result heading ("You win!" / "Bot wins" / "Player N wins") in the winner's color, a **verdict** micro-label (Domination / Nail-biter / Comeback / Clean sweep / Hard-fought win), a stats card (winning chain; biggest comeback or biggest chain; lead changes), a dim footer (duration · total turns), and Menu / Rematch buttons.

### 4.9 Toast

Bottom-center pill, `--text` fill on `--bg` text, slides up + fades in, auto-dismisses ~1.7s. Currently used to signal a live bot-difficulty change during a match ("Bot difficulty · Insane").

### 4.10 Settings controls

- **Toggle switch** (`.toggle`): 46×27 track, white knob; ON = `--p2` track, knob slides right. Used for Sound, Haptics.
- **Segmented control** (`.seg`): pill group on a `--tile` track; the selected button gets a `--surface` chip with a small shadow. Used for Animation (Full/Reduced/Off), Theme (Light/Dark), and Bot difficulty (full-width, 5 options).

---

## 5. Sound & haptics

Synthesized with the Web Audio API (no asset files); gated by the Sound setting.

| Cue | Sound | Haptic |
|---|---|---|
| Place an orb | triangle 440→600 Hz, ~0.11s, vol 0.16 | 8ms |
| Explosion (per wave) | square burst, pitch lowers as the chain deepens, ~0.22s | 14ms |
| Win | 4-note rising arpeggio (triangle) | `[20,40,20]` |

Haptics use `navigator.vibrate` where supported, gated by the Haptics setting. Audio context is created lazily on first user gesture (menu action or enabling Sound).

---

## 6. State → visual mapping (source of truth)

| Game state (PRD) | Visual channel |
|---|---|
| `owner` (NONE/P1/P2) | orb color (none / blue / coral) |
| `count` (0–3 stable) | pip count on the orb |
| active player (turn) | tile tint + legal-move highlight + turn pill dot |
| occupied-cell totals | control bar counts + ratio bar widths |
| explosion (`count 4`, transient) | `boom` + flying particles; never a static tile |
| game over / winner | end overlay (crown, heading, verdict, stats) |

Any new game state or sub-state gets a row here and a defined channel **before** it ships.

---

## 7. Modes & bot difficulty (UI surface)

- **Two modes** from the menu: vs a friend (hotseat) and vs the bot (bot = Player 2, coral).
- **Five difficulty tiers** in Settings, full-width segmented: Easy · Med · Hard · Expert · Insane. Presented left-to-right as increasing challenge. Difficulty changes apply live to the bot's next move; a toast confirms mid-game changes.
- While the bot decides, the turn pill reads "Bot is thinking…" and the board is non-interactive.

*(The bot's algorithm is implementation detail, not design; see the game file. This doc only governs how difficulty is presented.)*

---

## 8. Accessibility

- **Don't rely on hue alone.** Ownership (blue vs coral) is reinforced by the active-turn tint, the turn pill label, and the score bar; count is always a non-color channel (pips). Keep at least one non-color cue per state when adding skins.
- **Reduced/Off motion** is a first-class setting; honor it for any new animation.
- **Targets:** cells and controls are large; keep clickable cells comfortably tappable at the smallest supported width.
- **Contrast:** verify `--text`/`--dim` on their surfaces and white pips on orbs against WCAG in both themes when tuning colors.
- **Icon buttons** must keep `aria-label`s.
- **Future:** a color-blind-friendly option (shape/texture difference between the two players' orbs) remains a good addition.

---

## 9. Open items

- Persist settings across sessions (currently in-memory; resets on reload).
- Optional color-blind skin (per-player shape/texture).
- Win/overlay illustration or subtle celebration motion (kept minimal for now).
- Responsive breakpoints / minimum tile size formalized.
- Localizable copy pass.

---

## 10. Changelog

| Version | Date | Change |
|---|---|---|
| v1.0.1 | 2026-07-03 | Swapped player colors: Player 1 = blue, Player 2 / Bot = coral. |
| v1.0 | 2026-07-03 | Full rewrite for the sleek-minimal app: light/dark token system, menu/game/settings/end screens, buttons, turn pill, control+ratio bar, cell/orb/particle system, toggle + segmented controls, end overlay with verdict + stats, toast, Web Audio SFX + haptics, animation-speed system, and two-mode / five-tier difficulty presentation. Replaces the retired v0.1 (warm-palette single-board draft). |

*(Add a row for every UI/UX change; bump the version and "Last updated".)*
