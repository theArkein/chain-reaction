"""Reference implementation of Chain Reaction gameplay logic (PRD Sections 4-7).
Instrumented for validation: tracks max transient count, wave depth, empty-set
occurrences, and owner-conflict occurrences within a wave.
"""
from dataclasses import dataclass, field

N = 5
NONE, P1, P2 = 0, 1, 2
CAP = 3          # max stable capacity
THRESH = 4       # explode when count reaches this

def neighbors(r, c):
    out = []
    if r > 0: out.append((r-1, c))
    if r < N-1: out.append((r+1, c))
    if c > 0: out.append((r, c-1))
    if c < N-1: out.append((r, c+1))
    return out

@dataclass
class Stats:
    max_transient_count: int = 0
    max_waves: int = 0
    empty_set_events: int = 0
    owner_conflict_events: int = 0

class Board:
    def __init__(self):
        self.owner = [[NONE]*N for _ in range(N)]
        self.count = [[0]*N for _ in range(N)]

    def occupied(self):
        return [(r, c) for r in range(N) for c in range(N) if self.count[r][c] > 0]

    def owners_present(self):
        return {self.owner[r][c] for (r, c) in self.occupied()}

    def seed(self, r, c, player):
        assert self.owner[r][c] == NONE
        self.owner[r][c] = player
        self.count[r][c] = CAP

    def resolve(self, acting, stats: Stats):
        """Run wave-based cascade to completion. Returns number of waves."""
        waves = 0
        while True:
            exploding = [(r, c) for r in range(N) for c in range(N)
                         if self.count[r][c] >= THRESH]
            if not exploding:
                break
            waves += 1
            # Owner-conflict check: are all exploding cells owned by 'acting'?
            for (r, c) in exploding:
                if self.owner[r][c] != acting:
                    stats.owner_conflict_events += 1
            # Simultaneous application based on state at start of wave.
            # 1) reset all exploding cells
            for (r, c) in exploding:
                self.owner[r][c] = NONE
                self.count[r][c] = 0
            # 2) apply all neighbour increments/captures together
            deposits = {}  # (r,c) -> added count
            for (r, c) in exploding:
                for (nr, nc) in neighbors(r, c):
                    deposits[(nr, nc)] = deposits.get((nr, nc), 0) + 1
            for (nr, nc), add in deposits.items():
                self.owner[nr][nc] = acting     # unconditional capture
                self.count[nr][nc] += add
            # track transient max after this wave's application
            m = max((self.count[r][c] for r in range(N) for c in range(N)), default=0)
            stats.max_transient_count = max(stats.max_transient_count, m)
        stats.max_waves = max(stats.max_waves, waves)
        return waves

    def move(self, r, c, acting, stats: Stats):
        assert self.owner[r][c] == acting, "must select own cell"
        self.count[r][c] += 1
        self.resolve(acting, stats)
        # win check
        occ = self.occupied()
        if not occ:
            stats.empty_set_events += 1
            return "EMPTY_BOARD"
        owners = {self.owner[r][c] for (r, c) in occ}
        if len(owners) == 1:
            return f"WIN_{owners.pop()}"
        return None
