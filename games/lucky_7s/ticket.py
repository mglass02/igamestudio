import uuid, time
from games.lucky_7s.prize_table import TIERS
from core.math.prize_table import select_prize

def generate(wager_cents: int, player_id: str) -> dict:
    """
    GLI §4.4.12d: full outcome determined at purchase, not at reveal.
    GLI §4.14.2: all fields required for game recall.
    """
    tier = select_prize(TIERS)
    return {
        "ticket_id":   str(uuid.uuid4()),
        "player_id":   player_id,
        "created_at":  time.time(),
        "wager_cents": wager_cents,
        "prize_cents": int(wager_cents * tier.prize_multiplier) if tier else 0,
        "prize_tier":  tier.name if tier else None,
        "outcome":     "WIN" if tier else "LOSE",
        "revealed":    False,
        "game_state":  "PURCHASED",
        "game_id":     "lucky_7s_v1",
    }

def reveal(ticket: dict) -> dict:
    """§4.4.12d: reveal changes nothing — purely cosmetic."""
    if ticket["revealed"]:
        return ticket
    ticket["revealed"] = True
    ticket["reveal_time"] = time.time()
    ticket["game_state"] = "COMPLETE"
    return ticket
