from core.math.prize_table import PrizeTier, validate_rtp

# RTP contribution = prize_multiplier / frequency
# Target: ~70% total
TIERS = [
    PrizeTier("Grand Prize",  prize_multiplier=500,  frequency=100_000),  # 0.50%
    PrizeTier("Major Prize",  prize_multiplier=50,   frequency=500),      # 10.00%
    PrizeTier("Minor Prize",  prize_multiplier=10,   frequency=100),      # 10.00%
    PrizeTier("Small Prize",  prize_multiplier=3,    frequency=10),       # 30.00%
    PrizeTier("Free Ticket",  prize_multiplier=1,    frequency=5),        # 20.00%
]
# Total: 0.50 + 10.00 + 10.00 + 30.00 + 20.00 = 70.50%

if __name__ == "__main__":
    result = validate_rtp(TIERS)
    print(f"\nLucky 7s — RTP: {result['rtp_pct']} {'✓ COMPLIANT' if result['compliant'] else '✗ FAILS'}\n")
    for b in result["breakdown"]:
        print(f"  {b['tier']:<20} {b['frequency']:<20} contributes {b['contribution_pct']}")
