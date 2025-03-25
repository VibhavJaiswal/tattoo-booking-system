def estimate_duration(style: str, complexity: str) -> float:
    style = style.lower()
    complexity = complexity.lower()

    # Define rule-based duration estimates (in hours)
    estimates = {
        "realism": {"simple": 2.0, "medium": 3.0, "complex": 4.0},
        "minimalist": {"simple": 1.0, "medium": 1.5, "complex": 2.0},
        "watercolor": {"simple": 2.0, "medium": 2.5, "complex": 3.0},
        "traditional": {"simple": 2.0, "medium": 2.5, "complex": 3.5},
        "geometric": {"simple": 1.5, "medium": 2.0, "complex": 3.0},
    }

    # Try to get the estimate; fall back to default
    return estimates.get(style, {}).get(complexity, 2.0)


