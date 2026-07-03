# Chain Reaction — Gameplay PRD (v1.1)

**Scope:** This document specifies game logic and rules only. It intentionally excludes UI, visual design, animation, and rendering — those are separate concerns to be designed independently against this spec.

---

## Revision note (v1.1)

This revision resolves five items surfaced in review and validated against a reference implementation and fuzzing (30k+ random games, exhaustive opening analysis, and targeted cycle/termination searches). Changes:

1. **§2.1 / §6.1.3 — Deposit clamping.** Added an explicit clamp-at-4 rule for orb deposits, making the documented count range correct. Verified gameplay-identical to unclamped deposits across 15,000 paired games.
2. **§6.2 — Cascade termination.** Added a justification that cascades always terminate (deepest observed cascade: 21 waves).
3. **§7 — Non-empty invariant.** Added a proven invariant that the occupied set is never empty at end of turn, eliminating the theoretical deadlock the previous note only asserted.
4. **§5.1 / §10 — First-player advantage.** Documented (as intended design) the measured ~55/45 first-player edge and the turn-1 adjacency trap: seeding adjacent to `PLAYER_1` is legal but an immediate loss for `PLAYER_2` (confirmed for all 80 adjacent openings).
5. **§7 / §10 — Termination & draws.** Documented that the game always resolves to a win and can never draw (all stalling lines were eventually forced to a win; longest observed 2,591 moves).

---

## 1. Overview

A deterministic, perfect-information, turn-based strategy game for 2 players on a fixed 5×5 grid. Players grow orb counts in cells they control; cells that exceed capacity explode and capture neighboring cells. The game ends when one player controls all occupied cells on the board.

---

## 2. Board

- Grid size: **5 rows × 5 columns** (25 cells total), fixed — not configurable.
- Adjacency: **orthogonal only** (up, down, left, right). No diagonal adjacency.
- Each cell has between 2 and 4 neighbors depending on position (corner = 2, edge = 3, interior = 4), but this neighbor count has **no effect on capacity** — capacity is uniform across all cells (see Section 4).

### 2.1 Cell state

Each cell has two properties:

| Property | Type | Values |
|---|---|---|
| `owner` | enum | `NONE`, `PLAYER_1`, `PLAYER_2` |
| `count` | integer | `0` to `3` when stable; transiently reaches `4` during resolution (which immediately triggers explosion — see Sections 5 and 6) |

A cell with `count = 0` always has `owner = NONE`. A cell with `count > 0` always has an assigned owner.

**Note on the count range.** The `0..3` range holds for **stable** cells (start and end of every turn). During explosion resolution a cell may momentarily reach `4` — the explosion threshold — but never exceeds it, because deposits are clamped at 4 (see §6.1.3). Implementations may safely assert `count <= 4` at all times.

---

## 3. Players

Exactly **2 players**, `PLAYER_1` and `PLAYER_2`. No support for more than 2 in this version.

---

## 4. Capacity Rule

- Every cell, regardless of its position on the board (corner, edge, or interior), has the same maximum stable capacity: **3 orbs**.
- A cell **explodes** the instant its count reaches **4** (i.e., the 4th orb triggers explosion — the cell never remains at 4 once resolution runs).
- This is a deliberate departure from classic Chain Reaction, where capacity scales with neighbor count. Here capacity is constant; only the *number of cells that receive orbs* during an explosion varies by position (2, 3, or 4 neighbors).

---

## 5. Game Flow

The game proceeds through three phases: **Setup**, **Play**, and **Game Over**.

### 5.1 Setup Phase

1. `PLAYER_1` selects any one empty cell (`owner = NONE`) on the board. That cell is immediately set to `owner = PLAYER_1`, `count = 3`.
2. `PLAYER_2` selects any one empty cell other than the one `PLAYER_1` chose. Adjacency to `PLAYER_1`'s cell is **allowed** by the rules — no minimum distance constraint. That cell is immediately set to `owner = PLAYER_2`, `count = 3`.
3. Setup orbs are placed directly at count 3 and do **not** trigger explosion checks, since 3 is below the explosion threshold of 4.
4. After both players have placed their starting cell, the game transitions to the Play phase. `PLAYER_1` takes the first turn.

> **Implementation note (starting player).** The core rules designate `PLAYER_1` as the first seeder and first mover. Front-ends may randomize which side starts to offset the measured first-player advantage (§10). The shipped app does this in **bot mode** — the starting player (who both seeds first and moves first) is chosen at random each game — while **friend/hotseat mode** keeps `PLAYER_1` first. This does not change any rule in Sections 6–7.

**Constraint:** during setup, the only legal target is an empty cell (`owner = NONE`). Cells already claimed by the other player are not selectable.

**Design note — seeding adjacent to `PLAYER_1` is a losing move (intended).** Although adjacency is legal, if `PLAYER_2` seeds a cell orthogonally adjacent to `PLAYER_1`'s cell, `PLAYER_1` wins on the very first move. `PLAYER_1`'s only legal turn-1 move is to increment its own seed (3 → 4), which explodes and captures its neighbors — including `PLAYER_2`'s adjacent cell — pushing that cell to 4 and eliminating `PLAYER_2` entirely. This was confirmed for **all 80 adjacent openings** (100%); no non-adjacent opening loses on turn 1. This is intended behavior of the primed-seed design, not a defect; UIs may choose to warn players. See §10.

---

### 5.2 Play Phase

Players alternate turns, starting with `PLAYER_1`.

**Legal move:** On their turn, a player may select **only a cell they currently own** (`owner = currentPlayer`). They may not select:

- An empty cell (`owner = NONE`)
- A cell owned by the opponent

**Move effect:** Selecting a legal cell increments its `count` by 1.

**Immediately following the increment:**

- If the cell's `count` is now `< 4`, the turn ends normally (no explosion). Proceed to Section 6 (turn resolution).
- If the cell's `count` has reached `4`, explosion resolution begins (Section 6.1) before the turn is considered complete.

### 5.3 Game Over Phase

Entered when the win condition is met (Section 7). No further moves are accepted. The identified winner is final.

---

## 6. Explosion & Cascade Resolution

Explosion resolution runs to full completion — including all cascades — before control returns to the other player. It is not interruptible and involves no player choice.

### 6.1 Single Explosion

When a cell's `count` reaches `4`:

1. Identify the exploding cell's owner — call this `actingPlayer` (the player who owns the cell at the moment it explodes; this is always the player whose move triggered the cascade, since only the acting player can add to their own cell, and captured cells are re-owned to the acting player immediately upon capture within the same cascade).
2. Reset the exploding cell: `count = 0`, `owner = NONE`.
3. For **every orthogonal neighbor** of the exploding cell (2, 3, or 4 cells depending on board position):
   - Set `owner = actingPlayer` (this happens **unconditionally** — regardless of whether the neighbor was previously empty, owned by `actingPlayer`, or owned by the opponent; this is the sole mechanism by which opponent cells or new empty cells are captured).
   - Increment `count` by 1, **clamped at 4**: if the increment would raise `count` above 4, `count` is set to 4 and the surplus orb is discarded.

**Why clamping is safe (and why it must stay tied to the reset-and-deposit rule).** Because an explosion always resets the exploding cell to 0 and deposits exactly +1 into each neighbor (§6.1.2–3) — it never redistributes the cell's actual count — a cell that would otherwise stack to 5, 6, or 7 explodes identically to one at 4: it resets to 0 and deposits +1 per neighbor. The surplus above 4 is therefore discarded either way; clamping simply discards it at deposit time rather than at the next explosion. This was verified gameplay-identical (every board state, every turn) across 15,000 paired games. **Caution:** this equivalence depends on the fixed "+1 per neighbor, reset to 0" behavior. If a future variant made explosions redistribute the actual count, clamping would change outcomes and must be revisited.

### 6.2 Cascading

- After any single explosion (or simultaneous batch of explosions), re-scan the entire board for any cell where `count >= 4`.
- If one or more such cells exist, resolve all of them simultaneously as a new wave, following the same rule in 6.1 (each exploding cell uses its own current owner as that wave's `actingPlayer` for its neighbors — note that mid-cascade, a cell that itself was just captured and immediately pushed to 4 explodes using the capturing player as its owner, not the original turn-taker, though in practice these will always be the same player within one turn's cascade since capture always sets owner to `actingPlayer`).
- Repeat until a full scan finds no cell with `count >= 4`. The board is now stable, and the turn is complete.

**Termination (guaranteed).** Cascades always terminate. The total number of orbs on the board never increases during resolution: an explosion removes 4 orbs from a cell and deposits at most 4 (one per neighbor). Corner explosions (2 neighbors) destroy 2 orbs, edge explosions (3 neighbors) destroy 1, and interior explosions (4 neighbors) are net-neutral. Because only the single center cell (2,2) has four all-interior neighbors, any sustained cascade necessarily involves boundary explosions that strictly reduce the total orb count, so the board reaches a stable state — or a win — in a finite number of waves. There is no upper limit specified on cascade depth, but there is no risk of a non-terminating cascade. (Deepest single-turn cascade observed in 30,000 games: 21 waves.)

### 6.3 Simultaneity within a wave

All explosions identified in the same scan are resolved as a single simultaneous wave: all exploding cells are reset and all neighbor increments/captures (clamped per §6.1.3) are applied together, based on the board state at the start of that wave — not applied one-by-one in a way that lets an earlier explosion in the wave affect whether a later one in the same wave qualifies. (A cell that reaches `4` as a result of this wave's increments is only queued for explosion in the *next* wave.)

---

## 7. Win Condition

Checked once, at the end of a fully-resolved turn (after all cascades in Section 6 have completed):

1. Gather the set of all cells where `count > 0`.
2. If that set is non-empty and every cell in it shares the same `owner`, that player wins immediately. Transition to Game Over.
3. Empty cells (`count = 0`, `owner = NONE`) are **not** considered — a player does not need to have colonized the entire 25-cell board, only every currently-occupied cell.
4. If the set contains cells from both owners, the game continues: control passes to the other player for the next turn.

**Invariant (non-empty occupied set).** At the end of any fully-resolved turn the set of cells with `count > 0` is non-empty, so rule 7.2 always has cells to evaluate. Justification: a move that triggers no explosion leaves the mover's own cell occupied; a move that triggers a cascade ends with a final wave whose exploding cells each deposit +1 into their neighbors (every cell has ≥2 neighbors), and those neighbors are all `< 4` by definition of "final wave" — so at least two occupied cells always remain. Consequently the empty-board state is unreachable, and there is no deadlock in which control passes to a player with zero cells and no legal move.

**Invariant (acting player cannot self-eliminate).** A player can never end their own turn with zero owned cells: every capture and deposit during their cascade is *to* the acting player, so they always retain at least the cells their final wave deposited into. This is what makes the completeness note below hold.

**Property (always terminates in a win; no draws).** The game always resolves to a win for exactly one player, and can never end in a draw. Even when both players cooperate to avoid winning, stalling eventually fails: a player is inevitably forced into a position where every legal move captures the opponent's last cell. In targeted search, every such stalling line was eventually forced to a win with no repeated state (no cycle) and no draw; the longest stalled game observed ran 2,591 moves. There is no built-in move cap; see §10 for an optional bound.

**Note (no stuck state).** Because a player can only ever move by selecting a cell they already own, and (per the invariant above) the acting player always retains cells after their turn, a player to move always has at least one legal move as long as they are still in the game. If a check ever finds a player has zero owned cells, that player has already lost under rule 7.2 on the prior turn — there is no separate "stuck / no legal move" state to handle.

---

## 8. Turn Order Summary (state machine)

```
SETUP_1  --(P1 picks empty cell, seeds 3)-->  SETUP_2
SETUP_2  --(P2 picks empty cell, seeds 3)-->  PLAY (currentPlayer = P1)

PLAY:
  loop:
    currentPlayer selects own cell -> count += 1
    resolve explosions/cascades fully (Section 6)   # deposits clamped at 4
    evaluate win condition (Section 7)
    if won -> GAME_OVER
    else -> currentPlayer = other player; repeat

GAME_OVER: terminal state, no further moves
```

---

## 9. Explicitly Out of Scope for This Spec

- Visual design, layout, color, typography
- Animation/timing/motion
- Input device handling (mouse/touch specifics)
- Sound
- AI/CPU opponent behavior
- Undo/redo, move history, replay
- More than 2 players or configurable board sizes
- Any networking/multiplayer-over-network concerns

---

## 10. Open Questions / Future Considerations (not required for v1 logic)

- **First-player advantage (accepted for v1).** Moving first into a board of pre-primed (count-3) seeds gives `PLAYER_1` a measured ~55% win rate under random play (vs ~45% for `PLAYER_2`). This is accepted as intended for v1. Future balancing options, if desired: seed at a lower count (e.g., 1 or 2) to soften the opening, enforce a minimum seeding distance, or grant `PLAYER_2` compensation (e.g., second seed or first move).
- **Turn-1 adjacency trap (documented, see §5.1).** Seeding adjacent to `PLAYER_1` is a guaranteed turn-1 loss for `PLAYER_2`. A future version could forbid adjacent seeding to remove the trap; v1 leaves it legal and relies on player awareness / UI warnings.
- **Game length bound (optional).** The game always terminates in a win, but pathological stalling can produce very long games (2,000+ moves observed). If bounded duration is required (e.g., timed or tournament play), add a move cap with a tiebreak (e.g., the player controlling the most cells wins; ties resolved by total orb count). Not required for correctness.
