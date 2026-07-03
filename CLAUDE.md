# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A complete **Chain Reaction** game (2–4 players, configurable square board, plus a single-player bot) shipped as a single self-contained file (`index.html`) — HTML, CSS, and vanilla JS in one document, no build step, no dependencies, no framework. Open it directly in a browser to run it. Alongside it live two authoritative spec documents, a standalone prototype (`chain-reaction-lab.html`), and a folder of validation scripts.

## Commands

- **Run the game:** open `index.html` in any modern browser. There is no build, bundler, package manager, or dev server.
- **"Lint" the embedded game script** (there is no linter; this is the syntax gate used throughout development):
  ```
  awk '/<script>/{f=1;next} /<\/script>/{f=0} f' index.html > /tmp/game.js && node --check /tmp/game.js
  ```
- **Run a validation script** (all are standalone Python 3, no deps): `python3 validation/fuzz.py` (swap in any script name). See `validation/README.md` for what each one checks and its expected result.

## The three-artifact contract (read before changing anything)

The repo deliberately separates behavior, appearance, and implementation into three files that must stay in agreement:

- `Chain-Reaction-Gameplay-PRD-v1.2.md` — **source of truth for game logic/rules.** Sections 6–7 define explosion/cascade resolution and the win condition. Contains proven invariants (non-empty board, termination) and design decisions.
- `Chain-Reaction-Design-System-v2.0.md` — **source of truth for appearance and interaction.** Color/type/motion tokens, component specs, state→visual mapping.
- `index.html` — the implementation of both.

**Both spec docs carry an explicit maintenance rule: any change to the game must ship in the same change as the matching doc update, plus a changelog row.** When you modify `index.html`, update the relevant doc(s) too. Do not let them drift.

## Core game-logic rules that are easy to get wrong

- **Uniform capacity, clamp-at-4.** Every cell explodes at count 4 regardless of position. During a cascade wave, orb deposits into a cell are **clamped at 4** (`if(count[i]>THRESH) count[i]=THRESH`). This clamp is only safe because an explosion always resets the cell to 0 and deposits exactly +1 per neighbor — it does *not* redistribute the actual count. If you ever change explosions to carry the count forward, the clamp becomes wrong (see PRD §6.1.3). This equivalence was validated over 15k paired games (`validation/equiv.py`).
- **Simultaneous waves.** All cells at ≥4 in a scan explode together based on the board state at the start of that wave; cells pushed to ≥4 by the wave explode in the *next* wave (PRD §6.3).
- **Win check** runs only at the end of a fully-resolved turn: non-empty occupied set + single owning *team* (`teamsPresent()`, which equals owner in free-for-all) (PRD §7, §11.4).
- The JS resolution logic in `index.html` mirrors the validated Python reference `validation/engine.py`. Keep them equivalent; `validation/` exists to prove that.

## Implementation architecture (`index.html`, one IIFE)

- **Screens:** `home` (the match configurator) and `game`; plus a `prefs` bottom-sheet modal, an end `overlay` (child of `game`), and a `toast`. `setScreen(id)` toggles `.screen.active`. Game phases: `SETUP` → `PLAY` → game over.
- **Two config layers (this is the IA — don't merge them).** *Match setup* lives on the home screen and is **locked once a game starts**: mode, board size (`cfg.size`, 4–12), players (`cfg.players`, 2–4), format (`cfg.format`, `ffa`/`teams`). *Preferences* (the gear, reachable in-game) hold only global toggles — sound, haptics, animation, theme — plus **live bot difficulty during a bot game**.
- **Modes & seating:** `friend` (hotseat, 2–4 players, FFA or 2v2 teams) and `bot` (2 players; bot is `BOT=2`). Seat order (`seatOrder`) is shuffled each game for fairness — **except** 2-player hotseat, which stays P1-first. Eliminated players (0 cells) are skipped in the turn loop. The turn-order edge grows with player count (~55% first-seat at 2p → ~31% at 4p); randomized seating offsets it.
- **Board is size-parametric:** `S`×`S` with a rebuilt neighbor table `NB` (`buildNB`); all engine/bot functions loop over `S*S`. Cell gap and corner radius scale down as `S` grows.
- **Bot AI (2-player only):** pure functions (`simMove`, `evalBoard` with material + vulnerability + positional terms, `minimax` + alpha-beta, `orderedMoves`) and a `DIFF` tier table — Easy random, Medium/Hard fixed-depth, Expert/Insane iterative deepening within a time budget (`maxDepth`-capped). Difficulty is read live each move; mid-game changes take effect immediately (toast).
- **Rendering is diff-based** (`render()` mutates only changed cells) to avoid animation flicker — do not revert to full re-render. Animation timing flows through `speed()` (Full/Reduced/Off); Off skips particles and delays entirely.
- **Colors** are four CSS tokens `--p1`…`--p4` (P1 blue, P2 coral, P3 green, P4 amber); light/dark via `data-theme` on `<body>`. 2-player games render the ratio bar; 3–4 players render per-player HUD chips.
- **Audio** is synthesized via Web Audio (no asset files), created lazily on first user gesture; **no `localStorage`** — settings and match config are in-memory and reset on reload.
- **Mobile hardening:** viewport locked (no user zoom, `viewport-fit=cover`), `overscroll-behavior:none`, global `touch-action:manipulation`, disabled text selection/callout, iOS `gesture*` and `contextmenu` prevented in JS, `100dvh` sizing, and `env(safe-area-inset-*)` padding.

## Validation folder

`validation/` holds the Python reference engine (`engine.py`) and the scripts that back every claim in the PRD (fuzzing for termination/invariants, transient-count analysis, clamp equivalence, first-player/turn-1 analysis, cycle search). When changing game logic, re-run the relevant scripts and update expected results. `validation/README.md` is the index.
