"""Adversarially seek a transient count of 7.

Policy: strongly prefer moving on cells near the centre and on cells that
already have high counts, to try to force 4 simultaneous neighbour explosions
around a stable interior cell. Many restarts.
"""
import random

N = 5
NONE, P1, P2 = 0, 1, 2
THRESH = 4
CENTER = (2, 2)

def neighbors(r, c):
    out = []
    if r > 0: out.append((r-1, c))
    if r < N-1: out.append((r+1, c))
    if c > 0: out.append((r, c-1))
    if c < N-1: out.append((r, c+1))
    return out

def dist_center(r, c):
    return abs(r-2) + abs(c-2)

def resolve(owner, count, acting, box):
    while True:
        exploding = [(r, c) for r in range(N) for c in range(N) if count[r][c] >= THRESH]
        if not exploding:
            return
        for (r, c) in exploding:
            owner[r][c] = NONE; count[r][c] = 0
        deposits = {}
        for (r, c) in exploding:
            for nb in neighbors(r, c):
                deposits[nb] = deposits.get(nb, 0) + 1
        for (nr, nc), add in deposits.items():
            owner[nr][nc] = acting
            count[nr][nc] += add
            if count[nr][nc] > box[0]:
                box[0] = count[nr][nc]

def game(rng, box):
    owner = [[NONE]*N for _ in range(N)]
    count = [[0]*N for _ in range(N)]
    # bias seeds toward centre
    cells = sorted([(r, c) for r in range(N) for c in range(N)], key=lambda p: dist_center(*p))
    a = cells[rng.randrange(min(6, len(cells)))]
    owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
    rest = [x for x in cells if x != a]
    d = rest[rng.randrange(min(6, len(rest)))]
    owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3
    cur = P1
    for _ in range(3000):
        owned = [(r, c) for r in range(N) for c in range(N) if owner[r][c] == cur]
        if not owned:
            return
        # prefer high-count cells close to centre
        owned.sort(key=lambda p: (-count[p[0]][p[1]], dist_center(*p)))
        # pick among the top few with randomness
        k = min(3, len(owned))
        r, c = owned[rng.randrange(k)]
        count[r][c] += 1
        resolve(owner, count, cur, box)
        occ = [(r, c) for r in range(N) for c in range(N) if count[r][c] > 0]
        if not occ:
            return
        if len({owner[r][c] for (r, c) in occ}) == 1:
            return
        cur = P2 if cur == P1 else P1

box = [0]
rng = random.Random(7)
for _ in range(40000):
    game(rng, box)
    if box[0] >= 7:
        break
print("max transient found (adversarial):", box[0])
