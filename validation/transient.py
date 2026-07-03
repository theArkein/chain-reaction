"""Probe the true maximum transient count.

Two approaches:
1. Heavy random fuzz across many seeds, recording HOW the max arises
   (prior count of the cell + number of exploding neighbours).
2. A directed check: can we ever construct/reach a state where a stable
   interior cell at count 3 has all 4 neighbours exploding in one wave (=> 7)?
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

class Rec:
    def __init__(self):
        self.max_t = 0
        self.max_decomp = None  # (prior_count, num_exploding_neighbours, pos)
        self.saw7 = 0

def resolve(owner, count, acting, rec):
    while True:
        exploding = [(r, c) for r in range(N) for c in range(N) if count[r][c] >= THRESH]
        if not exploding:
            return
        expset = set(exploding)
        for (r, c) in exploding:
            owner[r][c] = NONE; count[r][c] = 0
        deposits = {}
        for (r, c) in exploding:
            for nb in neighbors(r, c):
                deposits[nb] = deposits.get(nb, 0) + 1
        for (nr, nc), add in deposits.items():
            prior = count[nr][nc]  # after resets; non-exploding cells kept their value
            owner[nr][nc] = acting
            count[nr][nc] += add
            newv = count[nr][nc]
            if newv > rec.max_t:
                rec.max_t = newv
                rec.max_decomp = (prior, add, (nr, nc))
            if newv >= 7:
                rec.saw7 += 1

def random_game(rng, rec):
    owner = [[NONE]*N for _ in range(N)]
    count = [[0]*N for _ in range(N)]
    cells = [(r, c) for r in range(N) for c in range(N)]
    a = rng.choice(cells); owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
    rest = [x for x in cells if x != a]
    d = rng.choice(rest); owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3
    cur = P1
    for _ in range(2000):
        owned = [(r, c) for r in range(N) for c in range(N) if owner[r][c] == cur]
        if not owned:
            return
        r, c = rng.choice(owned)
        count[r][c] += 1
        resolve(owner, count, cur, rec)
        occ = [(r, c) for r in range(N) for c in range(N) if count[r][c] > 0]
        if not occ:
            return
        if len({owner[r][c] for (r, c) in occ}) == 1:
            return
        cur = P2 if cur == P1 else P1

rec = Rec()
rng = random.Random(999)
GAMES = 20000
for _ in range(GAMES):
    random_game(rng, rec)
print(f"random fuzz games: {GAMES}")
print("max transient:", rec.max_t)
print("decomposition at max (prior_count, exploding_neighbours, pos):", rec.max_decomp)
print("times a value >=7 occurred:", rec.saw7)
