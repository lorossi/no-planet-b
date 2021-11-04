

from copy import deepcopy

from utils import smooth


class Square():
    """Class containing a square."""

    def __init__(self, x: int, y: int, scl: int, temperatures: list,
                 year: int) -> None:
        """Creates the square.

        Args:
            x (int): Top left x coordinate of the square
            y (int): Top left y coordinate of the square
            scl (int): Size of the square
            temperatures (list): List of normalized temperatures relative
            to the square
            year (int): Year relative to the square
        """
        self._x = x
        self._y = y
        self._scl = scl
        self._temperatures = deepcopy(temperatures)
        self._year = year
        # hard coded, there's no need to toggle this
        self._border = 0.1

    def getColor(self, temperature: float) -> tuple:
        """Get color relative to (interpolated) normalized temperature.

        Args:
            temperature (float): temperature in range [-1, 1]

        Returns:
            tuple: RGBA tuple
        """
        # blending constant
        color_blend = 0.85
        alpha_blend = 0.9

        # if temperature < 0, the color is blue
        if temperature < 0:
            channel = -temperature * color_blend + (1-color_blend)
            alpha = -temperature * alpha_blend + (1-alpha_blend)
            return (0, 0, channel, alpha)

        # otherwise, the color is red
        channel = temperature * color_blend + (1-color_blend)
        alpha = temperature * alpha_blend + (1-alpha_blend)
        return (channel, 0, 0, alpha)

    def interpolateTemperature(self, month: int,
                               percent: float) -> float:
        """Interpolate temperature according to current month
        and advancement in it.

        Args:
            month (int): Current month
            percent (float): Advancement percent

        Returns:
            float: Interpolated temperature in range [-1, 1]
        """
        # check that values are in range
        if month < 0 or month > 11:
            return None
        if percent < 0 or percent > 1:
            return None
        # compute next month
        next_month = (month + 1) % 12
        # extract temperature for current and next month
        # eventually wrapping around 12
        temperature = self._temperatures[month]
        next_temperature = self._temperatures[next_month]
        # interpolation with smoothing
        return temperature + (next_temperature - temperature) * \
            smooth(percent)

    @ property
    def x(self):
        return self._x + self._border / 2 * self._scl

    @ property
    def y(self):
        return self._y + self._border / 2 * self._scl

    @property
    def position(self):
        return (self.x, self.y)

    @ property
    def scl(self):
        return self._scl * (1-self._border)

    @property
    def external_scl(self):
        return self._scl
