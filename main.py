import requests

from typing import List
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


def parse_state(blobs) -> List[Reporting]:
    reports = []
    for blob in blobs:
        name = blob["county"]
        date = datetime.fromisoformat(blob["test_date"])
        cases = int(blob["new_positives"])
        tests = int(blob["total_number_of_tests"])
        if name == "Richmond":
            name = "Staten Island"
        if name == "Kings":
            name == "Brooklyn"
        reports.append(Reporting(name, date, cases, tests))
    return reports


def get_state_report(county: str, limit: int = 1) -> List[Reporting]:
    url = "https://health.data.ny.gov/api/id/xdss-u53e.json?$select=`test_date`,`county`,`new_positives`,`cumulative_number_of_positives`,`total_number_of_tests`,`cumulative_number_of_tests`\
    &$order=`:id`+DESC&$limit={limit}&$offset=0&county='{county}'"
    f_url = url.format(limit=limit, county=county)
    json = requests.get(f_url).json()
    return parse_state(json)


def compute_7mda(reports: List[Reporting]) -> List[Reporting]:
    new_reports: List[Reporting] = []
    for i, report in enumerate(reports):
        sum = 0.0
        for window in reports[i : i + 7]:
            sum += window.positivity
        report.moving_avg = sum / 7
        new_reports.append(report)
    return new_reports


def city_rate_by_borough(reports: List[Reporting]) -> Reporting:
    cases = 0
    tests = 0
    for report in reports:
        cases += report._cases
        tests += report._tests
    return Reporting("NYC", reports[0].date, cases, tests)


def get_state_data(days_prior, compute_mda):
    counties = ["New York", "Queens", "Kings", "Bronx", "Richmond"]
    reports_by_date = dict()
    test_dates = []
    if compute_mda:
        days_prior += 7
    for county in counties:
        reports = get_state_report(county, days_prior)
        for report in reports:
            if report._date in reports_by_date:
                reports_by_date[report._date].append(report)
            else:
                test_dates.append(report._date)
                reports_by_date[report._date] = [report]

    city_rate_by_date = []
    for date in sorted(reports_by_date.keys(), reverse=True):
        city_rate_by_date.append(city_rate_by_borough(reports_by_date[date]))
    rates_with_mda = compute_7mda(city_rate_by_date)
    for r in rates_with_mda[:7]:
        print(r)


# https://www.governor.ny.gov/news/governor-cuomo-details-covid-19-micro-cluster-metrics
# https://forward.ny.gov/percentage-positive-results-region-dashboard
if __name__ == "__main__":
    get_state_data(7, True)
