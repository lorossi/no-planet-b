import csv

from copy import deepcopy
from datetime import datetime

from utils import rescale


class Table:
    """Class handling the temperature data as in table."""

    def __init__(self, path: str) -> None:
        """Inits the table.

        Args:
            path (str): Path to the table
        """
        self._path = path
        self._rows = []
        self._year_data = {}
        self._normalized_year_data = {}

    def _loadRows(self, discard_header: bool = True) -> int:
        """Loads rows from table.

        Args:
            discard_header (bool, optional): If true, discard headers.
            Defaults to True.

        Returns:
            int: Number of loaded rows
        """
        # sourcery skip: assign-if-exp
        with open(self._path, "r") as f:
            reader = csv.reader(f)

            if discard_header:
                self._rows = list(reader)[1:]
            else:
                self._rows = list(reader)

        return len(self._rows)

    def _groupByYear(self, discard_current: bool = True) -> int:
        """Group temperatures by year

        Args:
            discard_current (bool, optional): Discard current year, as data
            might be incomplete. Defaults to True.

        Returns:
            int: Number of loaded years
        """

        current_year = datetime.now().year
        self._year_data = {}

        for row in self._rows:
            year = int(row[0][:-2])

            if discard_current and year == current_year:
                continue

            temperature = float(row[1])

            if year not in self._year_data:
                self._year_data[year] = []

            self._year_data[year].append(temperature)

        return len(self._year_data)

    def load(self) -> int:
        """Loads the table from file

        Returns:
            int: Number of loaded years
        """
        if self._loadRows() > 0:
            return self._groupByYear()

        return 0

    def normalizeTemperature(self) -> int:
        """Normalized temperature anomalies in range [-1, 1]

        Returns:
            int: Number of years
        """
        max_temp = max(float(r[1]) for r in self._rows)
        min_temp = min(float(r[1]) for r in self._rows)

        self._normalized_year_data = {}

        for year, temperatures in self._year_data.items():
            self._normalized_year_data[year] = [
                rescale(t, min_temp, max_temp, -1, 1) for t in temperatures
            ]

        return len(self._normalized_year_data)

    @property
    def year_data(self):
        return deepcopy(self._year_data)

    @property
    def normalized_year_data(self):
        return deepcopy(self._normalized_year_data)

    @property
    def first_year(self):
        return min(self._year_data)

    @property
    def last_year(self):
        return max(self._year_data)
