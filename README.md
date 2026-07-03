# Chain Reaction

A two-player **Chain Reaction** strategy game on a 5×5 grid. Grow orbs in cells you control; when a cell overflows it explodes and captures its neighbors, potentially setting off a chain. You win when you control every occupied cell on the board.

The entire game is one self-contained file — `chain-reaction.html` — with no build step, no dependencies, and no server. Just open it in a browser.

## Play

Open `chain-reaction.html` in any modern browser (double-click it, or drag it into a browser window).

From the menu you can play **with a friend** (two players, one device) or **against the bot**. Each player first places a starting cell, then players alternate: tap one of your own cells to add an orb. A cell explodes at 4 orbs, sending one orb to each orthogonal neighbor and converting them to your color — which can trigger further explosions. Last player standing on the board wins.

## Features

- **Two modes:** local hotseat (vs a friend) and single-player vs a bot.
- **Five bot difficulties:** Easy, Medium, Hard, Expert, and Insane. Expert and Insane use deep search and play near-optimally — Insane is meant to be effectively unbeatable.
- **Randomized opener in bot mode** to keep games fair (the first player is chosen at random each game); friend mode always starts with Player 1.
- **Sleek-minimal UI** with light and dark themes.
- **Settings:** sound, haptics, animation speed (Full / Reduced / Off), theme, and bot difficulty — all applied live. Changing difficulty mid-game shows a confirmation toast.
- **Synthesized sound and haptics** (Web Audio + vibration), no audio files.
- **Polished end screen** with a one-word verdict (Domination / Nail-biter / Comeback / Clean sweep / Hard-fought) and match stats.

## Repository layout

| Path | What it is |
|---|---|
| `chain-reaction.html` | The complete game (HTML + CSS + JS, single file). |
| `Chain-Reaction-Gameplay-PRD-v1.1.md` | Authoritative spec for the **game logic and rules** — cascade resolution, win condition, proven invariants, and design decisions. |
| `Chain-Reaction-Design-System-v1.0.md` | Authoritative spec for **appearance and interaction** — design tokens, components, motion, and state→visual mapping. |
| `validation/` | Standalone Python 3 scripts (and a reference engine) that verify the game logic and bot behavior. See `validation/README.md`. |
| `CLAUDE.md` | Guidance for AI assistants working in this repo. |

The two spec documents are the sources of truth: the PRD owns *behavior*, the design system owns *appearance*. Both include a maintenance rule requiring that any change to the game ship together with the matching doc update.

## Development

There is no build system. To edit the game, change `chain-reaction.html` directly and reload it in the browser.

Sanity-check the embedded script with:

```
awk '/<script>/{f=1;next} /<\/script>/{f=0} f' chain-reaction.html > /tmp/game.js && node --check /tmp/game.js
```

The game's cascade logic is a direct port of the validated Python reference in `validation/engine.py`. When changing game rules, re-run the relevant validation scripts (e.g. `python3 validation/fuzz.py`) and update their expected results — `validation/README.md` maps each script to the property it checks.

## Rules summary

- 5×5 grid, orthogonal adjacency only.
- Every cell holds up to 3 orbs; the 4th triggers an explosion.
- An explosion resets the cell to empty and adds one orb to each orthogonal neighbor, capturing them for the acting player. Chains resolve fully before the turn ends.
- A player wins when every occupied cell on the board is theirs.

Full details, including the simultaneous-wave resolution and the clamp-at-4 deposit rule, are in the gameplay PRD.
