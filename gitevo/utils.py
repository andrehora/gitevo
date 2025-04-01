import sys
import statistics
import os
import os.path as osp

from datetime import date
from gitevo.exceptions import BadGitRepo


def is_git_dir(d: str) -> bool:
    # From GitPython
    if osp.isdir(d):
        if (osp.isdir(osp.join(d, "objects")) or "GIT_OBJECT_DIRECTORY" in os.environ) and osp.isdir(
            osp.join(d, "refs")
        ):
            headref = osp.join(d, "HEAD")
            return osp.isfile(headref) or (osp.islink(headref) and os.readlink(headref).startswith("refs"))
        elif (
            osp.isfile(osp.join(d, "gitdir"))
            and osp.isfile(osp.join(d, "commondir"))
            and osp.isfile(osp.join(d, "gitfile"))
        ):
            raise BadGitRepo(d)
    return False

def stdout_msg(text: str) -> str:
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        green = '[92m'
        return f'\033{green}{text}\033[0m'
    return text

def stdout_link(text: str, url: str) -> str:
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        return f'\033]8;;{url}\a{text}\033]8;;\a'
    return text

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

def aggregate_basic(values: list[int|float], measure: str) -> int | float:
    if measure == 'max':
        return max(values)
    if measure == 'min':
        return min(values)
    return round(sum(values), 1)

def aggregate_stat(values: list[int|float], measure: str) -> int | float:
    operation = getattr(statistics, measure)
    result = operation(values)
    return round(result, 1)

def ensure_file_extension(extension: str | None):
    if extension is None:
        return None
    if not extension.startswith('.'):
        return f'.{extension}'
    return extension
    

class DateUtils:

    date_unit: str = 'year'
    
    @staticmethod
    def date_range(start_date: date, end_date: date) -> list[date]:
        assert end_date >= start_date
        if DateUtils.date_unit == 'month':
            return DateUtils._generate_months(start_date, end_date)
        # Default is year
        return DateUtils._generate_years(start_date, end_date)

    @staticmethod
    def formatted_dates(dates: list[date]) -> list[str]:
        if DateUtils.date_unit == 'month':
            return [each.strftime('%m/%Y') for each in dates]
        # Default is year
        return [each.strftime('%Y') for each in dates]
    
    @staticmethod
    def _generate_years(start_date: date, end_date: date) -> list[date]:
        month = 12
        dates = list(range(start_date.year, end_date.year+1))
        return [date(year, month, 1) for year in dates]

    @staticmethod
    def _generate_months(start_date: date, end_date: date, step: int = 1) -> list[date]:
        
        start_month = start_date.month
        start_year = start_date.year
        end_month = end_date.month
        end_year = end_date.year

        if start_year == end_year:
            dates = [(month, start_year) for month in range(start_month, end_month + 1, step)]
            return DateUtils._convert_tuples_to_dates(dates)

        start_year_months = [(month, start_year) for month in range(start_month, 13, step)]
        middle_years_months = [(month, year) for year in range(start_year + 1, end_year) for month in range(1, 13, step)]
        end_year_months = [(month, end_year) for month in range(1, end_month + 1, step)]

        return DateUtils._convert_tuples_to_dates(start_year_months + middle_years_months + end_year_months)

    @staticmethod
    def _convert_tuples_to_dates(dates: list[tuple[int,int]]) -> list[date]:
        return [date(year, month, 1) for month, year in dates]