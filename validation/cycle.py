"""Can the game go on forever?

The state space (board + player-to-move) is FINITE. So an infinite game exists
iff there is a reachable CYCLE of non-terminal states connected by legal moves.
If we ever revisit an identical (board, player-to-move) during a legal play line,
that proves an infinite game is possible.

Strategy: adversarially HUNT for a cycle. Each player, among its legal moves,
prefers (in order): a move that reproduces a state already seen in this line
(=> cycle), else a non-winning move, else any move. Many randomized restarts.
Also report the longest game length observed.
"""
import random

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
NB = {(r, c): neighbors(r, c) for r in range(N) for c in range(N)}

def resolve(owner, count, acting):
    while True:
        ex = [(r, c) for r in range(N) for c in range(N) if count[r][c] >= THRESH]
        if not ex:
            return
        for (r, c) in ex:
            owner[r][c] = NONE; count[r][c] = 0
        dep = {}
        for (r, c) in ex:
            for nb in NB[(r, c)]:
                dep[nb] = dep.get(nb, 0) + 1
        for (nr, nc), a in dep.items():
            owner[nr][nc] = acting
            count[nr][nc] += a
            if count[nr][nc] > THRESH:
                count[nr][nc] = THRESH

def key(owner, count, cur):
    flat = tuple(owner[r][c]*4 + count[r][c] for r in range(N) for c in range(N))
    return (flat, cur)

def winner(owner, count):
    occ = [(r, c) for r in range(N) for c in range(N) if count[r][c] > 0]
    if not occ:
        return "EMPTY"
    ow = {owner[r][c] for (r, c) in occ}
    return ow.pop() if len(ow) == 1 else None

def apply_move(owner, count, mv, cur):
    o2 = [row[:] for row in owner]
    c2 = [row[:] for row in count]
    c2[mv[0]][mv[1]] += 1
    resolve(o2, c2, cur)
    return o2, c2

def hunt(rng):
    owner = [[NONE]*N for _ in range(N)]
    count = [[0]*N for _ in range(N)]
    cells = [(r, c) for r in range(N) for c in range(N)]
    a = rng.choice(cells); owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
    d = rng.choice([x for x in cells if x != a]); owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3
    cur = P1
    seen = {}
    steps = 0
    seen[key(owner, count, cur)] = 0
    for steps in range(1, 15000):
        owned = [(r, c) for r in range(N) for c in range(N) if owner[r][c] == cur]
        if not owned:
            return ("lost_before", steps)  # shouldn't happen
        cyc = None; nonwin = None; anymv = None
        rng.shuffle(owned)
        for mv in owned:
            o2, c2 = apply_move(owner, count, mv, cur)
            nxt = P2 if cur == P1 else P1
            w = winner(o2, c2)
            k = key(o2, c2, nxt)
            anymv = (mv, o2, c2, nxt)
            if w in (P1, P2, "EMPTY"):
                continue  # terminal, avoid it
            if k in seen:
                cyc = (mv, o2, c2, nxt, seen[k]); break
            if nonwin is None:
                nonwin = (mv, o2, c2, nxt)
        if cyc is not None:
            return ("CYCLE", steps, steps - cyc[4])
        chosen = nonwin if nonwin is not None else anymv
        mv, o2, c2, nxt = chosen[:4]
        # if we were forced into a terminal (no non-terminal move existed)
        w = winner(o2, c2)
        if w in (P1, P2, "EMPTY"):
            return ("forced_end", steps)
        owner, count, cur = o2, c2, nxt
        seen[key(owner, count, cur)] = steps
    return ("maxsteps", steps)

rng = random.Random(4321)
longest = 0
cycles = 0
forced = 0
maxs = 0
RUNS = 30
for _ri in range(RUNS):
    res = hunt(rng)
    tag = res[0]
    print(f"run {_ri+1}: {tag} at step {res[1]}" + (f" cyclen={res[2]}" if tag=="CYCLE" else ""))
    if tag == "CYCLE":
        cycles += 1
        break
    elif tag == "forced_end":
        forced += 1
        longest = max(longest, res[1])
    elif tag == "maxsteps":
        maxs += 1
        longest = max(longest, res[1])
print(f"runs={RUNS}  cycles_found={cycles}  forced_to_end={forced}  hit_maxsteps={maxs}")
print(f"longest game (moves) observed while actively avoiding a win: {longest}")
