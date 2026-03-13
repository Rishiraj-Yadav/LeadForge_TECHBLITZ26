"""Lightweight heuristic scoring model placeholder."""

from app.utils.extraction import extract_budget_indicators


class LeadScoringModel:
    def predict(self, message: str, legitimacy_score: float) -> dict:
        budget = extract_budget_indicators(message)
        specificity_bonus = min(len(message.split()) / 20, 2)
        budget_bonus = min(len(budget["currency_amounts"]) * 1.2, 2.5)
        legitimacy_bonus = legitimacy_score * 0.5
        raw = 2.0 + specificity_bonus + budget_bonus + legitimacy_bonus
        score = max(0.0, min(10.0, round(raw, 1)))
        return {
            "score": score,
            "budget_indicators": budget["currency_amounts"] + budget["budget_keywords"],
        }
