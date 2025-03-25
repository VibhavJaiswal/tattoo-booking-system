def estimate_price_and_time(bounding_box, complexity_level):
    x_min, y_min, x_max, y_max = map(int, bounding_box)
    tattoo_area = (x_max - x_min) * (y_max - y_min)

    # Normalize based on a standard image size (640x480)
    normalized_area = tattoo_area / (640 * 480)

    # Complexity multipliers
    complexity_multiplier = {"simple": 1, "medium": 2, "complex": 3}

    # Base values
    base_price = 50  # USD
    base_time = 1.5  # Hours

    # Calculate
    estimated_price = base_price * normalized_area * complexity_multiplier.get(complexity_level, 1)
    estimated_time = base_time * normalized_area * complexity_multiplier.get(complexity_level, 1)

    return round(max(estimated_time, 1), 2), round(max(estimated_price, 50), 2)
