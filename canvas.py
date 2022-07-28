"""This file contains the class handling the canvas (single frame) creation."""

import cairo

from math import sqrt

from table import Table
from square import Square
from utils import get_color, interpolate_temperature, rescale


class Canvas:
    """Class handling the drawing."""

    def __init__(
        self, size: int = 1080, title_size: int = 100, border: float = 0.1
    ) -> None:
        """Create the drawing canvas.

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

        self._background_color = (0.96, 0.96, 0.96)
        self._text_color = (0.2, 0.2, 0.2)
        self._title_color = (0.05, 0.05, 0.05)

        self._title_font_size = self._title_size * 0.35
        self._subtitle_font_size = self._title_size * 0.2
        self._text_font_size = self._title_size * 0.15

        # load table
        self._table = Table("dataset/1880-2022.csv")

        # create canvas
        self._canvas = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self._width, self._height
        )
        # create drawing context
        self._ctx = cairo.Context(self._canvas)

    def _createLabels(self) -> None:
        """Create labels for all the texts in the frames."""
        self._labels = [
            "THERE IS NO PLAN B",
            "THERE IS NO PLANET B",
            "ACT NOW!",
            f"from {self._table.first_year}...",
            f"...to {self._table.last_year}",
        ]

    def _clearCanvas(self) -> None:
        """Clear and scales the drawing area."""
        # clears background
        self._ctx.rectangle(0, 0, self._width, self._height)
        self._ctx.set_source_rgb(*self._background_color)
        self._ctx.fill()
        # scale drawing to accomodate border
        self._ctx.translate(self._title_size / 2, self._title_size)
        self._ctx.translate(self._width / 2, self._height / 2)
        self._ctx.scale(1 - self._border, 1 - self._border)
        self._ctx.translate(-self._width / 2, -self._height / 2)

    def _saveCanvas(self) -> None:
        """Save canvas status."""
        self._ctx.save()

    def _restoreCanvas(self) -> None:
        """Restore canvas status."""
        self._ctx.restore()

    def loadMonths(self) -> None:
        """Load data for each individual month from the table."""
        self._months_loaded = True
        self._years_count = self._table.loadMonths()
        self._table.normalizeMonthlyTemperature()

    def loadYears(self) -> None:
        """Load data for each year from the table."""
        self._years_loaded = True
        self._years_count = self._table.loadYears()
        self._table.normalizeYearlyTemperature()

    def createSquares(self) -> None:
        """Create the squares and save them into the list. Each square is then rendered by itself."""
        if self._years_loaded == self._months_loaded:
            raise Exception("Both years and months have been loaded, or neither have.")

        # calculate number of rows and columns
        self._items = int(sqrt(self._years_count) + 0.5)
        # init container list
        self._squares = []

        # size of the square
        scl = min(
            self._width / self._items, (self._height - self._title_size) / self._items
        )

        # first year in the temperature data
        first_year = self._table.first_year
        # last year in the temperature data
        last_year = self._table.last_year

        # clear squares list
        self._squares = []

        # loop generating the square
        for i in range(self._items * self._items):
            # calculate current year and skip if
            # it's bigger than the latest year
            current_year = first_year + i
            if current_year > last_year:
                continue

            # calculate xy coordinates of the square
            x = i % self._items
            y = i // self._items

            # extract temperature data

            if self._table.normalized_yearly_data:
                # append the square to the list of squares
                self._squares.append(
                    Square(
                        x * scl,
                        y * scl,
                        scl,
                        self._table.normalized_yearly_data[current_year],
                    )
                )
            else:
                # terribly hacked together
                self._squares.append(
                    Square(
                        x * scl,
                        y * scl,
                        scl,
                    )
                )

    def _drawFrame(self, percent: float) -> None:
        """Draw a frame from the whole animation.

        Args:
            percent (float)
        """
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
            # get the color relative to the interpolated temperature
            color = get_color(interpolated)
            # draw the square
            self._ctx.set_source_rgba(*color)
            self._ctx.rectangle(s.x, s.y, s.scl, s.scl)
            self._ctx.fill()

    def _drawSingleFrame(self) -> None:
        """Draw a single frame, composing the output."""
        # load all temperature data
        temperatures = self._table.normalized_yearly_data
        first_year = self._table.first_year

        # preload font settings
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )

        self._ctx.set_font_size(self._text_font_size)
        self._ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

        # draw squares
        for x, s in enumerate(
            self._squares,
        ):
            # get the color relative to the interpolated temperature
            color = get_color(temperatures[first_year + x])

            # create the text
            prefix = "+" if s.temperature > 0 else ""
            temperature = f"{prefix}{s.temperature:.2f} °C"

            # calculate text sizes
            tw = self._ctx.text_extents(temperature).width
            th = self._ctx.text_extents(temperature).height
            dx = (s.scl - tw) / 2
            dy = (s.scl + th) / 2

            # calculate text color
            white_threshold = 0.5
            if abs(s.temperature) > white_threshold:
                ch = 0.9
            else:
                ch = 0.1

            # draw the square
            self._ctx.set_source_rgba(*color)
            self._ctx.rectangle(s.x, s.y, s.scl, s.scl)
            self._ctx.fill()

            # draw the text
            self._ctx.set_source_rgba(ch, ch, ch, 1)
            self._ctx.move_to(s.x + dx, s.y + dy)
            self._ctx.show_text(temperature)

    def _drawLabels(self) -> None:
        """Draw all the labels in the frame."""
        # calculate text position
        tx = self._squares[-1].x + self._squares[-1].scl * 1.1
        ty = self._squares[-1].y

        # set font
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )
        # set text color
        self._ctx.set_source_rgb(*self._text_color)
        # set text size
        self._ctx.set_font_size(self._subtitle_font_size)

        # getline height
        text_height = self._ctx.text_extents(self._labels[0]).height

        # write text lines at the end
        for i, line in enumerate(self._labels[:3]):
            self._ctx.move_to(tx, ty + text_height * (i + 1) * 1.5)
            self._ctx.show_text(line)

        # draw first year label
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        self._ctx.set_source_rgb(*self._text_color)

        # draw first year label
        scl = self._squares[-1].scl
        tx, ty = self._squares[0].position
        height = self._ctx.text_extents(self._labels[4]).height
        self._ctx.move_to(tx, ty - height)
        self._ctx.show_text(self._labels[3])

        # draw last year label
        tx, ty = self._squares[-1].position
        width = self._ctx.text_extents(self._labels[4]).width
        self._ctx.move_to(tx + scl - width, ty + scl + self._subtitle_font_size * 1.3)
        self._ctx.show_text(self._labels[4])

    def _drawTitle(self) -> None:
        """Draw the title and the subtitle of the frame."""
        self._title = "average Earth temperature, year by year"
        self._subtitle = (
            "the anomalies are evaluated with respect to the mean of all records"
        )

        # get size of the last square
        scl = self._squares[-1].scl

        # calculate text position
        tx = self._width * self._border / 2
        ty = scl * 0.75

        # set text color
        self._ctx.set_source_rgba(*self._title_color)
        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD
        )

        # write title
        self._ctx.set_font_size(self._title_font_size)
        self._ctx.move_to(tx + self._title_font_size / 4, ty)
        self._ctx.show_text(self._title)

        self._ctx.select_font_face(
            "Gilroy", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        # write sub title
        subtitle_height = self._ctx.text_extents(self._subtitle).height
        self._ctx.set_font_size(self._subtitle_font_size)

        self._ctx.move_to(
            tx + self._title_font_size / 2,
            ty + subtitle_height + self._subtitle_font_size * 0.25,
        )
        self._ctx.show_text(self._subtitle)

    def draw(self, frame: int = 0, duration: int = 0) -> None:
        """
        Draw the frame for the current month or for all months.

        If only a frame is being generated, no parameter needs to be passed.
        This could be refactored using a strategy pattern.

        Args:
            frame (int, optional): current frame being rendered. Defaults to 0.
            duration (int, optional): duration of the whole animation. Defaults to 0.
            write_temperatures (bool, optional): whether to write the temperatures. Defaults to False.
        """
        # save and clear the canvas
        self._saveCanvas()
        self._clearCanvas()

        if self._months_loaded:
            # calculate current percent
            percent = frame / (duration + 1)
            # draw the full frame
            self._drawFrame(percent)
        else:
            # draw the frame for the whole dataset
            self._drawSingleFrame()

        # draw all the labels
        self._createLabels()
        self._drawLabels()

        # restore position to write title relative to total area
        # and not drawing area
        self._restoreCanvas()

        # draw title
        self._drawTitle()

    def save(self, path: str = "output.png") -> None:
        """Save drawing to file.

        Args:
            path (str, optional): Path of the image. Defaults to "output.png".
        """
        self._canvas.write_to_png(path)
