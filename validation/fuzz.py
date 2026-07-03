import random
from engine import Board, Stats, N, NONE, P1, P2

def random_game(rng, stats):
    b = Board()
    # setup: two distinct empty cells
    cells = [(r, c) for r in range(N) for c in range(N)]
    a = rng.choice(cells)
    b.seed(*a, P1)
    rest = [x for x in cells if x != a]
    d = rng.choice(rest)
    b.seed(*d, P2)

    current = P1
    for _ in range(2000):  # generous cap to detect non-termination-ish runaway
        owned = [(r, c) for r in range(N) for c in range(N) if b.owner[r][c] == current]
        if not owned:
            # current player has no cells -> should already have lost previously
            return ("NO_MOVE", current)
        r, c = rng.choice(owned)
        res = b.move(r, c, current, stats)
        if res is not None:
            return (res, current)
        current = P2 if current == P1 else P1
    return ("TIMEOUT", current)

def main():
    rng = random.Random(12345)
    stats = Stats()
    outcomes = {}
    GAMES = 30000
    for i in range(GAMES):
        res, _ = random_game(rng, stats)
        outcomes[res] = outcomes.get(res, 0) + 1
    print(f"games: {GAMES}")
    print("outcomes:", outcomes)
    print("max_transient_count:", stats.max_transient_count)
    print("max_waves (single turn):", stats.max_waves)
    print("empty_set_events:", stats.empty_set_events)
    print("owner_conflict_events:", stats.owner_conflict_events)

if __name__ == "__main__":
    main()
