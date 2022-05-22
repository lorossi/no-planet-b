import cairo

from math import sqrt

from table import Table
from square import Square
from utils import get_month, get_colour, interpolate_temperature


class Canvas:
    """Class handling the drawing"""

    def __init__(
        self, size: int = 1080, title_size: int = 80, border: float = 0.1
    ) -> None:
        """Creates the drawing canvas.

        Args:
            size (int, optional): Size of the drawing area. Defaults to 1000.
            title_size (int, optional): Height of the title. Defaults to 80.
            border (float, optional): Border of the drawing area.
            Defaults to 0.1.
        """
        self._height = size + title_size
        self._width = size + title_size

        self._years_loaded = False
        self._months_loaded = False

        self._title_size = title_size
        self._border = border

        self._labels = ["THERE IS NO PLAN B", "THERE IS NO PLANET B"]

        # load table
        self._table = Table("dataset/1880-2021.csv")
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
        self._ctx.translate(self._title_size / 2, self._title_size)
        self._ctx.translate(self._width / 2, self._height / 2)
        self._ctx.scale(1 - self._border, 1 - self._border)
        self._ctx.translate(-self._width / 2, -self._height / 2)

    def _saveCanvas(self) -> None:
        """Saves canvas status."""
        self._ctx.save()

    def _restoreCanvas(self) -> None:
        """Restore canvas status."""
        self._ctx.restore()

    def loadMonths(self) -> None:
        self._months_loaded = True
        self._years_count = self._table.loadMonths()
        self._table.normalizeMonthlyTemperature()

    def loadYears(self) -> None:
        self._years_loaded = True
        self._years_count = self._table.loadYears()
        self._table.normalizeYearlyTemperature()

    def createSquares(self) -> None:
        """Creates the squares and saves them into the list."""

        if self._years_loaded == self._months_loaded:
            raise Exception("Both years and months have been loaded, or neither have.")

        # calculate number of rows and columns
        self._rows = self._cols = int(sqrt(self._years_count) + 0.5)
        # init container list
        self._squares = []

        # size of the square
        scl = min(
            self._width / self._cols, (self._height - self._title_size) / self._rows
        )
        # first year in the temperature data
        first_year = self._table.first_year
        # last year in the temperature data
        last_year = self._table.last_year

        # clear squares list
        self._squares = []

        # loop generating the square
        for i in range(self._cols * self._rows):
            # calculate current year and skip if
            # it's bigger than the latest year
            current_year = first_year + i
            if current_year > last_year:
                continue

            # calculate xy coordinates of the square
            x = i % self._rows
            y = i // self._rows

            # extract temperature data

            # append the square to the list of squares
            self._squares.append(
                Square(
                    x * scl,
                    y * scl,
                    scl,
                )
            )

    def draw(self, frame: int = 0, duration: int = 0) -> None:
        # save and clear the canvas
        self._saveCanvas()
        self._clearCanvas()

        if self._months_loaded:
            # calculate current percent
            percent = frame / (duration + 1)
            # calculate advancement in current month and
            # wrap in [0, 1) range
            month_percent = percent * 12
            while month_percent > 1:
                month_percent -= 1
            # calculate current and next month
            current_month = int(percent * 12)
            next_month = (current_month + 1) % 12
            # load all temperature data
            temperatures = self._table.normalized_monthly_data
            first_year = self._table.first_year

            # draw squares
            for x, s in enumerate(self._squares):
                current_temperature = temperatures[first_year + x][current_month]
                next_temperature = temperatures[first_year + x][next_month]
                # get the interpolated temperature relative to current month advancement
                interpolated = interpolate_temperature(
                    current_temperature, next_temperature, month_percent
                )
                # get the colour relative to the interpolated temperature
                colour = get_colour(interpolated)
                # draw the square
                self._ctx.set_source_rgba(*colour)
                self._ctx.rectangle(s.x, s.y, s.scl, s.scl)
                self._ctx.fill()
        else:
            # load all temperature data
            temperatures = self._table.normalized_yearly_data
            first_year = self._table.first_year
            # draw squares
            for x, s in enumerate(self._squares):
                # get the colour relative to the interpolated temperature
                colour = get_colour(temperatures[first_year + x])
                # draw the square
                self._ctx.set_source_rgba(*colour)
                self._ctx.rectangle(s.x, s.y, s.scl, s.scl)
                self._ctx.fill()

        # get size of the last rectangle
        scl = self._squares[-1].scl

        # calculate text size and position
        label_font_size = scl * 0.2
        tx, ty = self._squares[-1].position

        # set font
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        # set text colour
        self._ctx.set_source_rgba(0.05, 0.05, 0.05)
        # set text size
        self._ctx.set_font_size(label_font_size)

        # write first line
        self._ctx.move_to(tx + scl + label_font_size, ty + label_font_size * 1.5)
        self._ctx.show_text(self._labels[0])
        # write second line
        self._ctx.move_to(tx + scl + label_font_size, ty + label_font_size * 3)
        self._ctx.show_text(self._labels[1])

        # draw first year label
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        self._ctx.set_source_rgba(0.25, 0.25, 0.25)

        tx, ty = self._squares[0].position
        label = f"from {self._table.first_year}..."
        height = self._ctx.text_extents(label).height
        self._ctx.move_to(tx, ty - height)
        self._ctx.show_text(label)
        # draw last year label
        tx, ty = self._squares[-1].position
        label = f"... to {self._table.last_year}"
        width = self._ctx.text_extents(label).width
        self._ctx.move_to(tx + scl - width, ty + scl + label_font_size)
        self._ctx.show_text(label)

        # restore position to write title relative to total area
        # and not drawing area
        self._restoreCanvas()

        # calculate text size and position
        title_font_size = self._title_size * 0.5
        subtitle_font_size = title_font_size / 2
        tx = self._width * self._border / 2
        ty = scl * 0.75

        # set font
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )

        # set text colour
        self._ctx.set_source_rgba(0.05, 0.05, 0.05)

        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )

        # write title
        self._ctx.set_font_size(title_font_size)
        self._ctx.move_to(tx + title_font_size / 4, ty)

        if self._months_loaded:
            # get month name
            month_name = get_month(current_month)
            self._ctx.show_text(
                "temperature anomalies, year by year - " f"{month_name}"
            )
        else:
            self._ctx.show_text("temperature anomalies, year by year")

        # write sub title
        self._ctx.move_to(tx + title_font_size / 2, ty + title_font_size * 0.75)
        self._ctx.set_font_size(subtitle_font_size)
        self._ctx.show_text("each square represents a year")

    def save(self, path: str = "output.png") -> None:
        """Save drawing to file

        Args:
            path (str, optional): Path of the image. Defaults to "output.png".
        """
        self._canvas.write_to_png(path)
