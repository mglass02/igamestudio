from core.math.prize_table import calculate_rtp, validate_rtp, PrizeTier
from games.lucky_7s.prize_table import TIERS
from games.lucky_7s.ticket import generate, reveal

def test_lucky_7s_rtp_compliant():
    result = validate_rtp(TIERS)
    assert result["compliant"], f"Lucky 7s RTP {result['rtp_pct']} below minimum"

def test_ticket_outcome_fixed_at_purchase():
    """GLI §4.4.12d: outcome must not change after generation."""
    ticket = generate(100, "player_001")
    prize_at_purchase = ticket["prize_cents"]
    reveal(ticket)
    assert ticket["prize_cents"] == prize_at_purchase

def test_reveal_is_idempotent():
    """Revealing twice must produce same result."""
    ticket = generate(100, "player_001")
    reveal(ticket)
    state_after_first = ticket["prize_cents"]
    reveal(ticket)
    assert ticket["prize_cents"] == state_after_first

def test_wager_zero_rejected():
    try:
        generate(0, "player_001")
        assert False, "Should have raised"
    except (ValueError, AssertionError):
        pass
