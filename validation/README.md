# Chain Reaction — validation scripts

Reference implementation and simulations backing the fixes in `Chain-Reaction-Gameplay-PRD-v1.1.md`.
Pure Python 3, no dependencies. Run any script with `python3 <name>.py` from this folder.

| Script | What it validates | Key result |
|---|---|---|
| `engine.py` | Reference game engine (setup, play, simultaneous cascade, win check). Imported by the others. | — |
| `fuzz.py` | 30k random full games; tracks max transient count, wave depth, empty-set and owner-conflict events. | Gaps #1–#3: 0 empty-set, 0 conflicts; max transient 6; deepest cascade 21 waves. |
| `trace_2x2.py` | Wave-by-wave trace of the 2×2 example. | Gap #2: bottom-right reaches 5 mid-cascade. |
| `transient.py` | Measures how the max transient count arises. | Gap #2: max 6 = count-3 cell + 3 simultaneous neighbor explosions. |
| `seek7.py` | Adversarial search for a transient of 7. | Gap #2: never exceeded 5 under directed search. |
| `equiv.py` | Runs clamp-at-4 vs no-clamp on identical move sequences; compares every board. | Gap #2: 15k paired games, 0 mismatches — provably equivalent. |
| `balance.py` | P1 vs P2 win rates; exhaustive turn-1 opening analysis. | Gap #4: P1 ~55.5%; all 80 adjacent openings = P1 turn-1 win. |
| `cycle.py` | Hunts for a non-terminating game (state cycle) while avoiding the win. | Gap #5: 0 cycles, 0 draws; all stalling lines forced to a win (longest 2,591 moves). |

Note: `engine.py` and `equiv.py`/`balance.py`/`cycle.py` use the clamp-at-4 rule (§6.1.3); `fuzz.py`/`transient.py`/`trace_2x2.py`/`seek7.py` use unclamped deposits to demonstrate the transient-count behavior. Both are gameplay-equivalent (see `equiv.py`).
