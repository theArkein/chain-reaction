"""Quantify first-player advantage and turn-1 kills.

Metrics:
1. P1 vs P2 win rate under uniform random play.
2. Turn-1 win possibility: can P1 win on its very first move? Exhaustively
   check every (P1 seed, P2 seed) pair -> does P1's first explosion capture
   P2's only cell so that P1 wins immediately?
3. How the answer depends on whether P2 seeded adjacent to P1.
"""
import random
from itertools import product

N = 5
NONE, P1, P2 = 0, 1, 2
THRESH = 4

def neighbors(r, c):
    out = []
    if r > 0: out.append((r-1, c))
    if r < N-1: out.append((r+1, c))
    if c > 0: out.append((r, c-1))
    if c < N-1: out.append((r, c+1))
    return out

def resolve(owner, count, acting):
    while True:
        ex = [(r, c) for r in range(N) for c in range(N) if count[r][c] >= THRESH]
        if not ex:
            return
        for (r, c) in ex:
            owner[r][c] = NONE; count[r][c] = 0
        dep = {}
        for (r, c) in ex:
            for nb in neighbors(r, c):
                dep[nb] = dep.get(nb, 0) + 1
        for (nr, nc), a in dep.items():
            owner[nr][nc] = acting
            count[nr][nc] += a
            if count[nr][nc] > THRESH:
                count[nr][nc] = THRESH   # clamp-at-4 variant (equivalent)

def outcome(owner, count):
    occ = [(r, c) for r in range(N) for c in range(N) if count[r][c] > 0]
    if not occ:
        return "EMPTY"
    ow = {owner[r][c] for (r, c) in occ}
    return ow.pop() if len(ow) == 1 else None

# ---- 1. random win rates ----
def random_game(rng):
    owner = [[NONE]*N for _ in range(N)]
    count = [[0]*N for _ in range(N)]
    cells = [(r, c) for r in range(N) for c in range(N)]
    a = rng.choice(cells); owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
    d = rng.choice([x for x in cells if x != a]); owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3
    cur = P1
    for _ in range(3000):
        owned = [(r, c) for r in range(N) for c in range(N) if owner[r][c] == cur]
        if not owned:
            return P2 if cur == P1 else P1
        r, c = rng.choice(owned)
        count[r][c] += 1
        resolve(owner, count, cur)
        res = outcome(owner, count)
        if res in (P1, P2):
            return res
        cur = P2 if cur == P1 else P1
    return None

rng = random.Random(1)
w = {P1: 0, P2: 0, None: 0}
G = 40000
for _ in range(G):
    w[random_game(rng)] += 1
print(f"[random play] games={G}  P1 wins={w[P1]} ({100*w[P1]/G:.1f}%)  P2 wins={w[P2]} ({100*w[P2]/G:.1f}%)  draws/none={w[None]}")

# ---- 2 & 3. turn-1 win exhaustive over seed pairs ----
cells = [(r, c) for r in range(N) for c in range(N)]
def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

turn1_total = 0
turn1_wins = 0
wins_by_adjacency = {True: 0, False: 0}
pairs_by_adjacency = {True: 0, False: 0}
# P1 has exactly ONE move available on turn 1: its own seed cell. So the turn-1
# outcome is fully determined by the seed pair.
for a in cells:
    for d in cells:
        if a == d:
            continue
        owner = [[NONE]*N for _ in range(N)]
        count = [[0]*N for _ in range(N)]
        owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
        owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3
        count[a[0]][a[1]] += 1   # P1's only legal first move
        resolve(owner, count, P1)
        res = outcome(owner, count)
        adj = dist(a, d) == 1
        pairs_by_adjacency[adj] += 1
        turn1_total += 1
        if res == P1:
            turn1_wins += 1
            wins_by_adjacency[adj] += 1

print(f"[turn-1] seed pairs examined={turn1_total}  P1 immediate wins={turn1_wins} ({100*turn1_wins/turn1_total:.1f}%)")
print(f"[turn-1] when P2 seeded ADJACENT to P1: {wins_by_adjacency[True]}/{pairs_by_adjacency[True]} pairs -> P1 turn-1 win")
print(f"[turn-1] when P2 seeded NON-adjacent:   {wins_by_adjacency[False]}/{pairs_by_adjacency[False]} pairs -> P1 turn-1 win")
