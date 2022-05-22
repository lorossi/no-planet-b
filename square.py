class Square:
    """Class containing a square."""

    def __init__(self, x: int, y: int, scl: int) -> None:
        """Creates the square.

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
    def x(self):
        return self._x + self._border / 2 * self._scl

    @property
    def y(self):
        return self._y + self._border / 2 * self._scl

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def scl(self):
        return self._scl * (1 - self._border)

    @property
    def external_scl(self):
        return self._scl
