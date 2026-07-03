# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A complete two-player **Chain Reaction** game shipped as a single self-contained file (`index.html`) — HTML, CSS, and vanilla JS in one document, no build step, no dependencies, no framework. Open it directly in a browser to run it. Alongside it live two authoritative spec documents and a folder of validation scripts.

## Commands

- **Run the game:** open `index.html` in any modern browser. There is no build, bundler, package manager, or dev server.
- **"Lint" the embedded game script** (there is no linter; this is the syntax gate used throughout development):
  ```
  awk '/<script>/{f=1;next} /<\/script>/{f=0} f' index.html > /tmp/game.js && node --check /tmp/game.js
  ```
- **Run a validation script** (all are standalone Python 3, no deps): `python3 validation/fuzz.py` (swap in any script name). See `validation/README.md` for what each one checks and its expected result.

## The three-artifact contract (read before changing anything)

The repo deliberately separates behavior, appearance, and implementation into three files that must stay in agreement:

- `Chain-Reaction-Gameplay-PRD-v1.1.md` — **source of truth for game logic/rules.** Sections 6–7 define explosion/cascade resolution and the win condition. Contains proven invariants (non-empty board, termination) and design decisions.
- `Chain-Reaction-Design-System-v1.0.md` — **source of truth for appearance and interaction.** Color/type/motion tokens, component specs, state→visual mapping.
- `index.html` — the implementation of both.

**Both spec docs carry an explicit maintenance rule: any change to the game must ship in the same change as the matching doc update, plus a changelog row.** When you modify `index.html`, update the relevant doc(s) too. Do not let them drift.

## Core game-logic rules that are easy to get wrong

- **Uniform capacity, clamp-at-4.** Every cell explodes at count 4 regardless of position. During a cascade wave, orb deposits into a cell are **clamped at 4** (`if(count[i]>THRESH) count[i]=THRESH`). This clamp is only safe because an explosion always resets the cell to 0 and deposits exactly +1 per neighbor — it does *not* redistribute the actual count. If you ever change explosions to carry the count forward, the clamp becomes wrong (see PRD §6.1.3). This equivalence was validated over 15k paired games (`validation/equiv.py`).
- **Simultaneous waves.** All cells at ≥4 in a scan explode together based on the board state at the start of that wave; cells pushed to ≥4 by the wave explode in the *next* wave (PRD §6.3).
- **Win check** runs only at the end of a fully-resolved turn: non-empty occupied set + single owner (PRD §7).
- The JS resolution logic in `index.html` mirrors the validated Python reference `validation/engine.py`. Keep them equivalent; `validation/` exists to prove that.

## Implementation architecture (`index.html`, one IIFE)

- **Screen state machine:** `menu` / `game` / `settings` (modal) / end `overlay`; game phases are `SETUP` → `PLAY` → game over. Setup is order-agnostic, driven by a `starter` variable.
- **Modes:** `friend` (hotseat) and `bot`. In bot mode the bot is Player 2 and the **starting player is randomized each game** (friend mode keeps P1 first) — this offsets the measured ~55/45 first-player advantage.
- **Bot AI:** pure functions (`simMove`, `evalBoard`, `minimax` with alpha-beta, `orderedMoves`) plus a `DIFF` tier table. Easy = random, Medium/Hard = fixed-depth, Expert/Insane = iterative deepening within a time budget. Difficulty is read live each move, so mid-game changes take effect immediately (a toast signals this).
- **Rendering is diff-based** (`render()` mutates only changed cells) to avoid animation flicker — do not revert to full re-render. Animation timing flows through `speed()` (Full/Reduced/Off); Off skips particles and delays entirely.
- **Colors** are driven by `--p1`/`--p2` CSS tokens; swapping player colors = swapping those two token values. Light/dark via `data-theme` on `<body>`.
- **Audio** is synthesized via Web Audio (no asset files), created lazily on first user gesture; **no `localStorage`** — settings are in-memory and reset on reload.

## Validation folder

`validation/` holds the Python reference engine (`engine.py`) and the scripts that back every claim in the PRD (fuzzing for termination/invariants, transient-count analysis, clamp equivalence, first-player/turn-1 analysis, cycle search). When changing game logic, re-run the relevant scripts and update expected results. `validation/README.md` is the index.
