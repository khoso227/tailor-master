def calculate_remaining(total_val, advance_val):
    try:
        t = float(total_val) if total_val else 0
        a = float(advance_val) if advance_val else 0
        return t - a
    except ValueError:
        return 0