# Chain Reaction

A **Chain Reaction** strategy game for 2–4 players on a configurable square board. Grow orbs in cells you control; when a cell overflows it explodes and captures its neighbors, potentially setting off a chain. You win when your side controls every occupied cell on the board.

The entire game is one self-contained file — `index.html` — with no build step, no dependencies, and no server. Just open it in a browser.

**▶ Play online:** https://theArkein.github.io/chain-reaction/ (GitHub Pages)

## Play

Open `index.html` in any modern browser (double-click it, or drag it into a browser window).

The home screen is the match configurator: pick a mode and the relevant options appear, then press **Play**. Each player first places a starting cell, then players take turns: tap one of your own cells to add an orb. A cell explodes at 4 orbs, sending one orb to each orthogonal neighbor and converting them to your color — which can trigger further explosions. The last side with cells on the board wins.

## Features

- **Two modes:**
  - **Friends** — pass-and-play for **2–4 players** on one device, as **free-for-all** or **2v2 teams** (teams unlock at 4 players).
  - **Bot** — single-player vs the AI (2-player), on any board size.
- **Configurable board** — any square size from **4×4 to 12×12** (the board auto-scales; the cap keeps cells tappable on phones).
- **Five bot difficulties:** Easy, Medium, Hard, Expert, and Insane. Expert and Insane use deep search (iterative deepening) and play near-optimally — Insane is meant to be effectively unbeatable.
- **Fair openings** — seat order is randomized each game (classic Player-1-first is kept only for 2-player hotseat).
- **Adaptive, low-chrome UI** with light and dark themes; the board is the hero.
- **Preferences** (gear, available in-game): sound, haptics, animation speed (Full / Reduced / Off), and theme. Bot difficulty is also adjustable live during a bot game (with a toast). Match setup (board/players/format) is chosen on the home screen and locked once a game starts.
- **Synthesized sound and haptics** (Web Audio + vibration), no audio files.
- **Polished end screen** with a one-word verdict (Domination / Nail-biter / Comeback / Clean sweep / Hard-fought) and match stats.
- **Mobile-hardened** — no pinch/double-tap zoom, no scroll rubber-banding, no text selection or long-press menus, and safe-area padding for notches.

## Repository layout

| Path | What it is |
|---|---|
| `index.html` | The complete game (HTML + CSS + JS, single file). |
| `chain-reaction-lab.html` | Standalone hotseat prototype for the generalized game (board size, 2–4 players, FFA/teams) — a sandbox that predates the merge into `index.html`. |
| `Chain-Reaction-Gameplay-PRD-v1.2.md` | Authoritative spec for the **game logic and rules** — cascade resolution, win condition, proven invariants, and the generalization (players/teams/board size). |
| `Chain-Reaction-Design-System-v2.0.md` | Authoritative spec for **appearance and interaction** — design tokens, components, motion, and state→visual mapping. |
| `validation/` | Standalone Python 3 scripts (and a reference engine) that verify the game logic and bot behavior. See `validation/README.md`. |
| `CLAUDE.md` | Guidance for AI assistants working in this repo. |

The two spec documents are the sources of truth: the PRD owns *behavior*, the design system owns *appearance*. Both include a maintenance rule requiring that any change to the game ship together with the matching doc update.

## Development

There is no build system. To edit the game, change `index.html` directly and reload it in the browser.

Sanity-check the embedded script with:

```
awk '/<script>/{f=1;next} /<\/script>/{f=0} f' index.html > /tmp/game.js && node --check /tmp/game.js
```

The game's cascade logic is a direct port of the validated Python reference in `validation/engine.py`. When changing game rules, re-run the relevant validation scripts (e.g. `python3 validation/fuzz.py`) and update their expected results — `validation/README.md` maps each script to the property it checks.

## Rules summary

- Square board (default 5×5, configurable 4×4–12×12), orthogonal adjacency only.
- Every cell holds up to 3 orbs; the 4th triggers an explosion.
- An explosion resets the cell to empty and adds one orb to each orthogonal neighbor, capturing them for the acting player. Chains resolve fully before the turn ends.
- A side (player, or team in 2v2) wins when every occupied cell on the board belongs to it. Players with no cells are eliminated; the game always ends in a win (never a draw).

Full details — the simultaneous-wave resolution, the clamp-at-4 deposit rule, and the multiplayer/teams/board-size generalization — are in the gameplay PRD.
