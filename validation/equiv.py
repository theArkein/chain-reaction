"""Prove clamp-at-4 and no-clamp produce identical games.

Two engines, identical move sequences. After every turn, compare the full
(owner, count) board. Also compare final outcomes.
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

def resolve(owner, count, acting, clamp):
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
            if clamp and count[nr][nc] > THRESH:
                count[nr][nc] = THRESH   # cap at 4, discard extra

def outcome_after(owner, count):
    occ = [(r, c) for r in range(N) for c in range(N) if count[r][c] > 0]
    if not occ:
        return "EMPTY"
    owners = {owner[r][c] for (r, c) in occ}
    return f"WIN_{owners.pop()}" if len(owners) == 1 else None

def play(rng):
    # build two boards
    boards = []
    for _ in range(2):
        boards.append(([[NONE]*N for _ in range(N)], [[0]*N for _ in range(N)]))
    cells = [(r, c) for r in range(N) for c in range(N)]
    a = rng.choice(cells); rest = [x for x in cells if x != a]; d = rng.choice(rest)
    for (owner, count) in boards:
        owner[a[0]][a[1]] = P1; count[a[0]][a[1]] = 3
        owner[d[0]][d[1]] = P2; count[d[0]][d[1]] = 3

    cur = P1
    for _ in range(2000):
        # choose move from board 0 (both boards are identical at this point -> invariant we check)
        o0, c0 = boards[0]
        owned = [(r, c) for r in range(N) for c in range(N) if o0[r][c] == cur]
        if not owned:
            return ("NO_MOVE_MISMATCH" if False else "done", None)
        mv = rng.choice(owned)
        results = []
        for i, (owner, count) in enumerate(boards):
            count[mv[0]][mv[1]] += 1
            resolve(owner, count, cur, clamp=(i == 0))
            results.append(outcome_after(owner, count))
        # compare boards fully (stable states must match)
        o0, c0 = boards[0]; o1, c1 = boards[1]
        if o0 != o1 or c0 != c1:
            return ("BOARD_MISMATCH", (mv, cur))
        if results[0] != results[1]:
            return ("OUTCOME_MISMATCH", results)
        if results[0] is not None:
            return ("ok_win", results[0])
        cur = P2 if cur == P1 else P1
    return ("timeout", None)

rng = random.Random(2024)
mismatches = 0
wins = 0
GAMES = 15000
for _ in range(GAMES):
    tag, info = play(rng)
    if tag in ("BOARD_MISMATCH", "OUTCOME_MISMATCH"):
        mismatches += 1
        print("MISMATCH:", tag, info)
    elif tag == "ok_win":
        wins += 1
print(f"games: {GAMES}, clean wins: {wins}, mismatches: {mismatches}")
