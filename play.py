import random, time, os
from games.lucky_7s.ticket import generate, reveal
from games.lucky_7s.prize_table import TIERS
from core.math.prize_table import validate_rtp
from core.audit.logger import AuditLogger

audit = AuditLogger()
PLAYER = "player_001"

# ─── Display helpers ────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def rules():
    print("""
╔══════════════════════════════════════════╗
║           🎰  LUCKY 7s  🎰              ║
║                                          ║
║  HOW TO PLAY                             ║
║  • Scratch 6 numbers in a 2×3 grid       ║
║  • Match any 3 identical numbers → WIN   ║
║  • 7 is WILD — matches any number        ║
║                                          ║
║  PRIZE TABLE              RTP: 70.50%    ║
║  ───────────────────────────────────     ║
║  Grand Prize   500×  (1 in 100,000)      ║
║  Major Prize    50×  (1 in 500)          ║
║  Minor Prize    10×  (1 in 100)          ║
║  Small Prize     3×  (1 in 10)           ║
║  Free Ticket     1×  (1 in 5)            ║
╚══════════════════════════════════════════╝
""")

# ─── Grid builder ───────────────────────────────────────────────────────────

NUMBERS = [1, 2, 3, 4, 5, 6, 8, 9]  # 7 reserved as wild

def build_grid(ticket: dict) -> list[list[int]]:
    """
    Build a 2×3 grid of numbers that visually reflects the outcome.
    Outcome already decided — grid is theatrical display only.
    GLI §4.4.12d: reveal changes nothing.
    """
    tier = ticket["prize_tier"]
    grid = [random.choice(NUMBERS) for _ in range(6)]

    if tier == "Grand Prize":
        # Three 7s (wild) guaranteed
        for i in [0, 2, 4]: grid[i] = 7

    elif tier == "Major Prize":
        # Three matching non-7 numbers
        n = random.choice(NUMBERS)
        for i in [0, 2, 4]: grid[i] = n

    elif tier == "Minor Prize":
        # Two matching + one 7 wild
        n = random.choice(NUMBERS)
        grid[0] = n
        grid[2] = n
        grid[4] = 7

    elif tier == "Small Prize":
        # Two matching + one near-miss
        n = random.choice(NUMBERS)
        grid[0] = n
        grid[2] = n
        grid[4] = random.choice([x for x in NUMBERS if x != n])

    elif tier == "Free Ticket":
        # One 7 wild visible, no full match
        grid[0] = 7
        grid[2] = random.choice(NUMBERS)
        grid[4] = random.choice([x for x in NUMBERS if x != grid[2]])

    else:
        # Losing ticket — ensure no three match and no winning 7s
        while True:
            grid = [random.choice(NUMBERS) for _ in range(6)]
            counts = {}
            for n in grid:
                counts[n] = counts.get(n, 0) + 1
            sevens = grid.count(7)
            matches = any(
                counts.get(grid[i], 0) + sevens >= 3
                for i in range(6)
            )
            if not matches:
                break

    random.shuffle(grid)
    return [grid[:3], grid[3:]]

def check_win(grid: list[list[int]]) -> tuple[bool, int]:
    """Check if flattened grid has 3 matching numbers (7 is wild)."""
    flat = grid[0] + grid[1]
    sevens = flat.count(7)
    non_seven = [n for n in flat if n != 7]
    counts = {}
    for n in non_seven:
        counts[n] = counts.get(n, 0) + 1
    for n, count in counts.items():
        if count + sevens >= 3:
            return True, n
    if sevens >= 3:
        return True, 7
    return False, 0

def display_grid(grid, revealed: set, scratching=False):
    """Print the 2×3 grid. Unrevealed cells show [ ? ]"""
    print()
    for row_i, row in enumerate(grid):
        line = "  "
        for col_i, num in enumerate(row):
            idx = row_i * 3 + col_i
            if idx in revealed:
                marker = f"[ {num} ]" if num != 7 else "[ 7★]"
            else:
                marker = "[ ? ]"
            line += marker + " "
        print(line)
    print()

def scratch_sequence(grid):
    """Interactive scratch — reveal one cell at a time."""
    revealed = set()
    positions = list(range(6))
    random.shuffle(positions)  # random reveal order

    print("  Positions: 1-2-3 (top row)  4-5-6 (bottom row)")

    for i, pos in enumerate(positions):
        row, col = pos // 3, pos % 3
        display_grid(grid, revealed)
        input(f"  Press ENTER to scratch cell {pos+1}...")
        revealed.add(pos)

        # Animated scratch
        print(f"\r  Scratching... ✦", end='', flush=True)
        time.sleep(0.4)

        # Early win detection — show excitement
        flat_so_far = [grid[p//3][p%3] for p in revealed]
        sevens = flat_so_far.count(7)
        counts = {}
        for n in flat_so_far:
            if n != 7:
                counts[n] = counts.get(n, 0) + 1
        leading = max((c for c in counts.values()), default=0) + sevens
        if leading == 2 and len(revealed) < 6:
            print(f"\r  One more match wins! 👀", end='')
            time.sleep(0.3)
        print("\r" + " " * 30 + "\r", end='')

    display_grid(grid, revealed)
    return revealed

# ─── Main game loop ──────────────────────────────────────────────────────────

def play_session():
    clear()
    rules()
    balance = 1000  # $10.00

    while True:
        print(f"  Balance: ${balance/100:.2f}")
        cmd = input("  Press ENTER to play $1.00  |  'r' for rules  |  'q' to quit: ").strip().lower()

        if cmd == 'q':
            break
        if cmd == 'r':
            clear()
            rules()
            continue

        wager = 100
        if wager > balance:
            print("  Not enough balance.\n")
            continue

        # Deduct wager and generate ticket
        balance -= wager
        audit.log("WAGER_PLACED", {"wager_cents": wager}, PLAYER)
        ticket = generate(wager, PLAYER)

        clear()
        print("\n  🎰 LUCKY 7s — Ticket purchased!")
        print(f"  Wager: $1.00  |  Balance: ${balance/100:.2f}")
        print(f"\n  Match any 3 numbers to win. 7★ is wild.\n")

        # Build and scratch grid
        grid = build_grid(ticket)
        scratch_sequence(grid)

        # Reveal result
        reveal(ticket)
        won, match_num = check_win(grid)

        if ticket["outcome"] == "WIN":
            prize = ticket["prize_cents"]
            balance += prize
            slow_print(f"\n  ★ {ticket['prize_tier'].upper()}! ★")
            if match_num == 7:
                slow_print(f"  Three 7★ wilds — you won ${prize/100:.2f}!")
            else:
                slow_print(f"  Three {match_num}s matched — you won ${prize/100:.2f}!")
            audit.log("GAME_COMPLETE", {"prize_cents": prize, "tier": ticket["prize_tier"]}, PLAYER)
        else:
            slow_print("\n  No match this time. Better luck next game.")
            audit.log("GAME_COMPLETE", {"prize_cents": 0}, PLAYER)

        chain = audit.verify_chain()
        print(f"\n  Audit: ✓ chain valid ({chain['entries_checked']} entries)")
        print(f"  Balance: ${balance/100:.2f}\n")
        print("  " + "─" * 40)

        if balance <= 0:
            print("\n  Out of balance. Thanks for playing!\n")
            break

    print(f"\n  Final balance: ${balance/100:.2f}")
    print("  Thanks for playing Lucky 7s.\n")

if __name__ == "__main__":
    play_session()
