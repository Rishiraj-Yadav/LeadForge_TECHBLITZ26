"""Simple close probability estimator."""


def close_probability(score: float, stage: str) -> float:
    stage_weight = {
        "new": 0.1,
        "contacted": 0.25,
        "qualified": 0.45,
        "proposal": 0.65,
        "negotiation": 0.8,
        "won": 1.0,
        "lost": 0.0,
    }.get(stage, 0.2)
    return round(min(1.0, (score / 10) * 0.7 + stage_weight * 0.3), 2)
