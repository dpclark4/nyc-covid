from datetime import datetime

class Reporting:
    moving_avg: float
    def __init__(self, name: str, date: datetime, cases: int, tests: int):
        self._name = name
        self._date = date
        self._cases = cases
        self._tests = tests
        self._positivity = round(cases / tests * 100, 2)

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def cases(self) -> int:
        return self._cases

    @property
    def tests(self) -> int:
        return self._tests

    @property
    def positivity(self) -> float:
        return self._positivity

    @property
    def moving_avg(self):
        return self._moving_avg

    @moving_avg.setter
    def moving_avg(self, mda: float):
        self._moving_avg = round(mda, 2)

    def to_str(self) -> str:
        date = self._date.strftime("%Y-%m-%d")
        if self._moving_avg:
            return f"{date} {self._name}: {self.positivity:.2f} - 7MDA: {self._moving_avg:.2f}"
        return f"{date} {self._name}: {self.positivity}"

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return self.to_str()
