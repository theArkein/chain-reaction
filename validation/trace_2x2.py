"""Trace the user's 2x2 scenario, wave by wave.
2x2 block at (0,0)=TL (0,1)=TR (1,0)=BL (1,1)=BR, all P1, all count 3.
Player plays TL.
"""
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

owner = [[NONE]*N for _ in range(N)]
count = [[0]*N for _ in range(N)]
for (r, c) in [(0,0),(0,1),(1,0),(1,1)]:
    owner[r][c] = P1; count[r][c] = 3

def show(label):
    print(label)
    for r in range(3):
        print("  " + " ".join(str(count[r][c]) for c in range(3)) + "   (showing top-left 3x3)")
    print()

show("initial (TL TR / BL BR all = 3)")
# player plays TL
count[0][0] += 1
print(">>> player increments TL to", count[0][0], "\n")

wave = 0
while True:
    exploding = [(r, c) for r in range(N) for c in range(N) if count[r][c] >= THRESH]
    if not exploding:
        break
    wave += 1
    print(f"WAVE {wave}: exploding = {exploding}")
    for (r, c) in exploding:
        owner[r][c] = NONE; count[r][c] = 0
    deposits = {}
    for (r, c) in exploding:
        for nb in neighbors(r, c):
            deposits[nb] = deposits.get(nb, 0) + 1
    for (nr, nc), add in deposits.items():
        owner[nr][nc] = P1
        count[nr][nc] += add
    # report the cell of interest
    print(f"   deposits applied: {deposits}")
    print(f"   BR(1,1) count is now {count[1][1]}")
    show(f"after wave {wave}")

print("FINAL max cell value observed for BR reached above.")
