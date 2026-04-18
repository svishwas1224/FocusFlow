from .config import FOCUS_CATEGORY_WEIGHTS


def calculate_focus_score(category: str, event_rate: float, forbidden: bool = False) -> int:
    category_weight = FOCUS_CATEGORY_WEIGHTS.get(category, 0.5)
    activity_score = min(max(event_rate / 10 * 100, 0), 100)
    if forbidden:
        category_weight *= 0.15
    score = int((category_weight * 0.6 + activity_score / 100 * 0.4) * 100)
    return max(0, min(score, 100))


def classify_situation(category: str, focus_score: int) -> str:
    if focus_score >= 80 and category == "focus":
        return "deep_work"
    if focus_score < 40 or category == "distractor":
        return "distraction"
    return "productive"


def event_density_to_rate(events: int, sample_seconds: float) -> float:
    if sample_seconds <= 0:
        return 0.0
    return events / sample_seconds
