
def clamp(val, min_val, max_val):
    return min(max(val, min_val), max_val)


def lerp(start, end, interpolation_amount):
    return start + (end - start) * interpolation_amount


def inverse_lerp(start, end, interpolation_amount):
    return lerp(start, end, 1 / interpolation_amount)