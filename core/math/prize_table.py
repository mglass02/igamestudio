from dataclasses import dataclass
from typing import Optional

@dataclass
class PrizeTier:
    name: str
    prize_multiplier: float   # prize = wager * multiplier
    frequency: int            # 1-in-N tickets wins this tier

def calculate_rtp(tiers: list[PrizeTier]) -> float:
    return sum(t.prize_multiplier / t.frequency for t in tiers)

def validate_rtp(tiers: list[PrizeTier], min_rtp: float = 0.70) -> dict:
    rtp = calculate_rtp(tiers)
    return {
        "rtp": rtp,
        "rtp_pct": f"{rtp*100:.2f}%",
        "compliant": rtp >= min_rtp,
        "breakdown": [
            {
                "tier": t.name,
                "frequency": f"1 in {t.frequency:,}",
                "contribution_pct": f"{t.prize_multiplier/t.frequency*100:.3f}%"
            }
            for t in tiers
        ]
    }

def select_prize(tiers: list[PrizeTier]) -> Optional[PrizeTier]:
    """
    GLI §4.5.2b: do not modify or discard RNG outcomes.
    Each tier checked independently against its frequency.
    """
    from core.rng.core import randbelow
    for tier in tiers:
        if randbelow(tier.frequency) == 0:
            return tier
    return None  # losing ticket
