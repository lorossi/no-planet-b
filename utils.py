"""File containing a bunch of functions used in the whole project."""


def rescale(
    value: float, old_min: float, old_max: float, new_min: float, new_max: float
) -> float:
    """Map value to a new range.

    Args:
        value (float): Value to be mapped
        old_min (float)
        old_max (float)
        new_min (float)
        new_max (float)

    Returns:
        float:
    """
    return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min


def poly_smooth(x: float, n: float = 3) -> float:
    """Polynomial easing of a variable in range [0, 1].

    Args:
        x (float): variable to be smoothed
        n (float, optional): polynomial degree. Defaults to 3.

    Returns:
        float: _description_
    """
    if x > 1:
        return 1
    if x < 0:
        return 0

    if x < 0.5:
        return pow(2, n - 1) * pow(x, n)

    return 1 - pow(-2 * x + 2, n) / 2


def get_colour(temperature: float) -> tuple[float, float, float, float]:
    """Get colour from temperature.

    Args:
        temperature (float): Temperature in range [-1, 1]
    Return
        tuple: RGBA tuple
    """
    # blending constant
    colour_blend = 0.85
    alpha_blend = 0.9

    # if temperature < 0, the colour is blue
    if temperature < 0:
        channel = -temperature * colour_blend + (1 - colour_blend)
        alpha = -temperature * alpha_blend + (1 - alpha_blend)
        return (0, 0, channel, alpha)

    # otherwise, the colour is red
    channel = temperature * colour_blend + (1 - colour_blend)
    alpha = temperature * alpha_blend + (1 - alpha_blend)
    return (channel, 0, 0, alpha)


def interpolate_temperature(current_t: float, next_t: float, percent: float) -> float:
    """Interpolate temperature according to the relative percent.

    Args:
        current_t (float): current month temperature
        next_t (float): next month temperature
        percent (float): current evaluation percent

    Returns:
        float
    """
    smooth_percent = poly_smooth(percent)
    return (1 - smooth_percent) * current_t + smooth_percent * next_t
