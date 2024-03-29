"""File handling the data parsing and manipulation."""

import csv

from utils import rescale
from datetime import date


class Table:
    """Class handling the temperature data as in table."""

    def __init__(self, path: str) -> None:
        """Init the table.

        Args:
            path (str): Path to the table
        """
        self._current_year = date.today().year
        self._path = path
        self._rows = []
        self._monthly_data = {}
        self._normalized_monthly_data = {}
        self._normalized_yearly_data = {}
        self._yearly_data = {}
        self._monthly_data = {}

    def _loadRows(self, discard_header: bool = True) -> int:
        """Load rows from table.

        Args:
            discard_header (bool, optional): If true, discard headers.
            Defaults to True.

        Returns:
            int: Number of loaded rows
        """
        with open(self._path, "r") as f:
            reader = csv.reader(f)

            if discard_header:
                self._rows = list(reader)[1:]
            else:
                self._rows = list(reader)

        return len(self._rows)

    def _groupByMonth(self, discard_current: bool = True) -> int:
        """Group temperatures by month for each year.

        Args:
            discard_current (bool, optional): Discard current year, as data
            might be incomplete. Defaults to True.

        Returns:
            int: Number of loaded years
        """
        self._monthly_data = {}

        for row in self._rows:
            year = int(row[0][:-2])

            if discard_current and year == self._current_year:
                continue

            temperature = float(row[1])

            if year not in self._monthly_data:
                self._monthly_data[year] = []

            self._monthly_data[year].append(temperature)

        return len(self._monthly_data)

    def _groupByYear(self, discard_current: bool = True) -> int:
        """Group temperatures by year.

        Args:
            discard_current (bool, optional): Discard current year, as data
            might be incomplete. Defaults to True.

        Returns:
            int: Number of loaded years
        """
        self._yearly_data = {}

        for row in self._rows:
            year = int(row[0][:-2])

            if discard_current and year == self._current_year:
                continue

            temperature = float(row[1])

            if year not in self._yearly_data:
                self._yearly_data[year] = 0

            self._yearly_data[year] += temperature

        for year in self._yearly_data:
            self._yearly_data[year] /= 12

        return len(self._yearly_data)

    def loadMonths(self) -> int:
        """Load the table from file, differentiating data by month.

        Returns:
            int: Number of loaded years
        """
        if self._loadRows() > 0:
            return self._groupByMonth()

        return 0

    def loadYears(self) -> int:
        """Load the table from file, averaging the temperature anomaly of each year.

        Returns:
            int: Number of loaded years
        """
        if self._loadRows() > 0:
            return self._groupByYear()

        return 0

    def normalizeMonthlyTemperature(self) -> int:
        """Normalize temperature anomalies in range [-1, 1].

        Returns:
            int: Number of years
        """
        max_temp = max(float(r[1]) for r in self._rows)
        min_temp = min(float(r[1]) for r in self._rows)

        for year, temperatures in self._monthly_data.items():
            self._normalized_monthly_data[year] = [
                rescale(t, min_temp, max_temp, -1, 1) for t in temperatures
            ]

        return len(self._normalized_monthly_data)

    def normalizeYearlyTemperature(self) -> int:
        """Normalize temperature anomalies in range [-1, 1].

        Returns:
            int: Number of years
        """
        max_temp = max(self._yearly_data.values())
        min_temp = min(self._yearly_data.values())

        for year, temperature in self._yearly_data.items():
            self._normalized_yearly_data[year] = rescale(
                temperature, min_temp, max_temp, -1, 1
            )

        return len(self._normalized_yearly_data)

    @property
    def monthly_data(self) -> dict[int, list[float]]:
        """Return monthly data for each year.

        Returns:
            dict[int, list[float]]
        """
        return self._monthly_data

    @property
    def normalized_monthly_data(self) -> dict[int, list[float]]:
        """Return normalized monthly data for each year.

        Returns:
            dict[int, list[float]]
        """
        return self._normalized_monthly_data

    @property
    def yearly_data(self) -> dict[int, float]:
        """Return yearly data for each year.

        Returns:
            dict[int, list[float]]
        """
        return self._yearly_data

    @property
    def normalized_yearly_data(self) -> dict[int, float]:
        """Return normalized data for each year.

        Returns:
            dict[int, float]
        """
        return self._normalized_yearly_data

    @property
    def first_year(self) -> int:
        """Return first year of data.

        Returns:
            int
        """
        if self._monthly_data:
            return min(self._monthly_data.keys())

        return min(self._yearly_data.keys())

    @property
    def last_year(self) -> int:
        """Return last year of data.

        Returns:
            int
        """
        if self._monthly_data:
            return max(self._monthly_data.keys())

        return max(self._yearly_data.keys())
