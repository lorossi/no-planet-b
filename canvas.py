import cairo

from math import sqrt

from table import Table
from square import Square
from utils import get_month


class Canvas():
    """Class handling the drawing"""

    def __init__(self, size: int = 1000, title_size: int = 100,
                 border: float = 0.1) -> None:
        """Creates the drawing canvas.

        Args:
            size (int, optional): Size of the drawing area. Defaults to 1000.
            title_size (int, optional): Height of the title. Defaults to 100.
            border (float, optional): Border of the drawing area.
            Defaults to 0.1.
        """
        self._width = size
        self._height = size + title_size
        self._title_size = title_size
        self._border = border

        # load and normalize temperature data
        self._t = Table("dataset/1880-2021.csv")
        self._items = self._t.load()
        self._t.normalizeTemperature()

        # calculate number of rows and columns
        self._rows = self._cols = int(sqrt(self._items) + 0.5)
        # init container list
        self._squares = []
        # create canvas
        self._canvas = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self._width, self._height
        )
        # create drawing context
        self._ctx = cairo.Context(self._canvas)

    def _clearCanvas(self) -> None:
        """Clears and scales the drawing area"""
        # clears background
        self._ctx.rectangle(0, 0, self._width, self._height)
        self._ctx.set_source_rgb(0.94, 0.94, 0.94)
        self._ctx.fill()
        # scale drawing to accomodate border
        self._ctx.translate(0, self._title_size)
        self._ctx.translate(self._width / 2, self._height / 2)
        self._ctx.scale(1 - self._border, 1 - self._border)
        self._ctx.translate(- self._width / 2, - self._height / 2)

    def _saveCanvas(self) -> None:
        """Saves canvas status."""
        self._ctx.save()

    def _restoreCanvas(self) -> None:
        """Restore canvas status."""
        self._ctx.restore()

    def createSquares(self) -> None:
        """Creates the squares and saves them into the list."""
        # size of the square
        scl = min(self._width / self._cols, self._width / self._rows)
        # first year in the temperature data
        first_year = self._t.first_year
        # last year in the temperature data
        last_year = self._t.last_year

        # clear squares list
        self._squares = []

        # loop generating the square
        for i in range(self._cols * self._rows):
            # calculate current year and exit if
            # it's bigger than the lastest year
            current_year = first_year + i
            if current_year > last_year:
                continue

            # calculate xy coordinates of the square
            x = i % self._rows
            y = i // self._rows
            # append the square to the list of squares
            self._squares.append(
                Square(
                    x * scl, y * scl, scl,
                    self._t.normalized_year_data.get(current_year),
                    current_year
                )
            )

    def draw(self, frame: int, duration: int) -> None:
        """Draws a frame of the animation.

        Args:
            frame (int): Current frame
            duration (int): Total duration of the animation
        """
        # save and clear the canvas
        self._saveCanvas()
        self._clearCanvas()

        # calculate current percent
        percent = frame / (duration + 1)
        # calculate advancement in current month and
        # wrap in [0, 1) range
        month_percent = (percent * 12)
        while month_percent > 1:
            month_percent -= 1
        # calculate current month
        month = int(percent * 12)

        # draw squares
        for s in self._squares:
            # get the interpolated temperature relative to current month
            # advancement
            interpolated = s.interpolateTemperature(month, month_percent)
            # get the color relative to the interpolated temperature
            color = s.getColor(interpolated)
            # draw the square
            self._ctx.set_source_rgba(*color)
            self._ctx.rectangle(s.x, s.y, s.scl, s.scl)
            self._ctx.fill()

        # get size and external size of the last rectangle
        scl = self._squares[-1].scl
        ext_scl = self._squares[-1].external_scl
        # calculate text size and position
        label_font_size = scl * 0.275
        tx, ty = self._squares[-1].position

        # set font
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD
        )
        # set text color
        self._ctx.set_source_rgba(0.05, 0.05, 0.05)
        # set text size
        self._ctx.set_font_size(label_font_size)

        # write first line
        self._ctx.move_to(tx + scl + label_font_size,
                          ty + label_font_size * 1.5)
        self._ctx.show_text("THERE IS NO PLAN B")
        # write second line
        self._ctx.move_to(tx + scl + label_font_size,
                          ty + ext_scl - label_font_size)
        self._ctx.show_text("THERE IS NO PLANET B")

        # draw first year label
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL
        )
        self._ctx.set_source_rgba(0.25, 0.25, 0.25)

        tx, ty = self._squares[0].position
        label = "from 1880..."
        self._ctx.move_to(tx, ty - label_font_size * 0.3)
        self._ctx.show_text(label)
        # draw last year label
        tx, ty = self._squares[-1].position
        label = "...to 2020"
        self._ctx.move_to(tx - len(label) * 1.5, ty + scl + label_font_size)
        self._ctx.show_text(label)

        # restore position to write title relative to total area
        # and not drawing area
        self._restoreCanvas()

        # calculate text size and position
        title_font_size = self._title_size * 0.5
        subtitle_font_size = title_font_size / 2
        tx = self._width * self._border / 2
        ty = scl * .75

        # set font
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD
        )

        # set text color
        self._ctx.set_source_rgba(0.05, 0.05, 0.05)

        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL
        )
        # get month name
        month_name = get_month(month)
        # write title
        self._ctx.set_font_size(title_font_size)
        self._ctx.move_to(tx + title_font_size / 4, ty)
        self._ctx.show_text(
            "temperature anomalies, year by year - "
            f"{month_name}"
        )

        # write sub title
        self._ctx.move_to(
            tx + title_font_size / 2,
            ty + title_font_size * 0.75
        )
        self._ctx.set_font_size(subtitle_font_size)
        self._ctx.show_text(
            "each square represents a year"
        )

    def save(self, path: str = "output.png") -> None:
        """Save drawing to file

        Args:
            path (str, optional): Path of the image. Defaults to "output.png".
        """
        self._canvas.write_to_png(path)
