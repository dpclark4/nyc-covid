import requests

from reporting import Reporting
from typing import List
from datetime import datetime


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


def simple_mda(report: Reporting, trailing_reports: List[Reporting]) -> Reporting:
    new_report = report
    sum = 0.0
    assert len(trailing_reports) == 7
    for window in trailing_reports:
        sum += window.positivity
    new_report.moving_avg = sum / 7
    return new_report


def all_mda(report: Reporting, trailing_reports: List[Reporting]) -> Reporting:
    new_report = report
    cases = 0
    tests = 0
    assert len(trailing_reports) == 7
    for window in trailing_reports:
        cases += window.cases
        tests += window.tests
    new_report.moving_avg = cases / tests * 100
    return new_report


def compute_7mda(reports: List[Reporting]) -> List[Reporting]:
    new_reports: List[Reporting] = []
    for i, report in enumerate(reports[:7]):
        new_reports.append(all_mda(report, reports[i : i + 7]))
    return new_reports


def city_rate_by_borough(reports: List[Reporting]) -> Reporting:
    cases = 0
    tests = 0
    for report in reports:
        cases += report.cases
        tests += report.tests
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
