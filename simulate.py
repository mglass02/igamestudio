from games.lucky_7s.ticket import generate
from games.lucky_7s.prize_table import TIERS
from core.math.prize_table import validate_rtp

PLAYS = 100_000
WAGER = 100
total_wagered = 0
total_prizes = 0
wins_by_tier = {}

for i in range(PLAYS):
    ticket = generate(WAGER, "sim_player")
    total_wagered += WAGER
    total_prizes += ticket["prize_cents"]
    if ticket["prize_tier"]:
        wins_by_tier[ticket["prize_tier"]] = wins_by_tier.get(ticket["prize_tier"], 0) + 1

actual_rtp = total_prizes / total_wagered * 100
theoretical_rtp = validate_rtp(TIERS)["rtp"] * 100

print(f"\nLucky 7s — {PLAYS:,} play simulation")
print(f"─────────────────────────────────")
print(f"Total wagered:    ${total_wagered/100:>10,.2f}")
print(f"Total prizes:     ${total_prizes/100:>10,.2f}")
print(f"Actual RTP:       {actual_rtp:>10.2f}%")
print(f"Theoretical RTP:  {theoretical_rtp:>10.2f}%")
print(f"Variance:         {abs(actual_rtp - theoretical_rtp):>10.2f}%")
print(f"\nWins by tier:")
for tier, count in sorted(wins_by_tier.items(), key=lambda x: -x[1]):
    pct = count / PLAYS * 100
    print(f"  {tier:<20} {count:>6,} times  ({pct:.2f}%)")
