import requests

from typing import List
from datetime import datetime


class Reporting:
    def __init__(self, name: str, date: datetime, cases: int, tests: int):
        self.name = name
        self.date = date
        self.cases = cases
        self.tests = tests
        self.positivity = round(cases / tests * 100, 2)

    def __str__(self) -> str:
        date = self.date.strftime("%Y-%m-%d")
        return f"{date} {self.name}: {self.positivity}"

    def __repr__(self) -> str:
        date = self.date.strftime("%Y-%m-%d")
        return f"{date} {self.name}: {self.positivity}"


def parse_state(blob) -> Reporting:
    name = blob["county"]
    date = datetime.fromisoformat(blob["test_date"])
    cases = int(blob["new_positives"])
    tests = int(blob["total_number_of_tests"])
    if name == "Richmond":
        name = "Staten Island"
    if name == "Kings":
        name == "Brooklyn"
    return Reporting(name, date, cases, tests)


def get_state_report(county: str, limit: int = 1) -> Reporting:
    url = "https://health.data.ny.gov/api/id/xdss-u53e.json?$select=`test_date`,`county`,`new_positives`,`cumulative_number_of_positives`,`total_number_of_tests`,`cumulative_number_of_tests`&$order=`:id`+DESC&$limit={limit}&$offset=0&county='{county}'"
    f_url = url.format(limit=limit, county=county)
    json = requests.get(f_url).json()[0]
    return parse_state(json)


def compute_citywide(reports: List[Reporting]) -> Reporting:
    cases = 0
    tests = 0
    for report in reports:
        cases += report.cases
        tests += report.tests
    return Reporting("NYC", reports[0].date, cases, tests)


def get_state_data():
    counties = ["New York", "Queens", "Kings", "Bronx", "Richmond"]
    data = dict()
    date = None
    for county in counties:
        report = get_state_report(county)
        if report.date in data:
            data[report.date].append(report)
        else:
            date = report.date
            data[report.date] = [report]
    all = compute_citywide(data[date])
    print(all)


if __name__ == "__main__":
    get_state_data()
