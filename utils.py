from math import cos, pi


def rescale(value: float, old_min: float, old_max: float,
            new_min: float, new_max: float) -> float:
    """Map value to a new range

        Args:
            value (float): Value to be mapped
            old_min (float)
            old_max (float)
            new_min (float)
            new_max (float)

        Returns:
            float:
        """
    return (value - old_min) * (new_max - new_min) / \
        (old_max - old_min) + new_min


def smooth(x: float) -> float:
    """Cubic interpolation of a value in range [0, 1]

    Args:
        x (float): Value to be smoothed

    Returns:
        float
    """
    if x > 1 or x < 0:
        return None

    return -(cos(pi * x) - 1) / 2


def get_month(x: int) -> str:
    """Get month name from its index in range [0, 11]

    Args:
        x (int): Month index

    Returns:
        str: Month name
    """
    if x < 0 or x > 11:
        return None

    return ["january", "february", "march", "april", "may", "june", "july",
            "august", "september", "october", "november", "december"][x]
