"""File containing the class handling a square. This is not more complicated than a dataclass."""


class Square:
    """Class containing a square."""

    def __init__(self, x: int, y: int, scl: int) -> None:
        """Create the square.

        Args:
            x (int): Top left x coordinate of the square
            y (int): Top left y coordinate of the square
            scl (int): Size of the square
        """
        self._x = x
        self._y = y
        self._scl = scl

        # hard coded, there's no need to toggle this
        self._border = 0.1

    @property
    def x(self) -> float:
        """Top left corner x coordinate of the square.

        Returns:
            float
        """
        return self._x + self._border / 2 * self._scl

    @property
    def y(self) -> float:
        """Top left corner y coordinate of the square.

        Returns:
            float
        """
        return self._y + self._border / 2 * self._scl

    @property
    def position(self) -> tuple[float, float]:
        """Position of the top left corner.

        Returns:
            tuple[float, float]: x and y coordinates
        """
        return (self.x, self.y)

    @property
    def scl(self) -> float:
        """Size of the rectangle.

        Returns:
            float
        """
        return self._scl * (1 - self._border)
