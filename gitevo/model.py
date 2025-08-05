from datetime import date

from gitevo.info import MetricInfo
from gitevo.utils import aggregate_basic, aggregate_stat, DateUtils

class MetricEvolution:

    def __init__(self, name: str, dates: list[str], values: list):
        self.name = name
        self.dates = dates
        self.values = values

    @property
    def values_as_str(self) -> list[str]:
        return [str(value) for value in self.values]
    
    @property
    def dates_and_values(self):
        return list(zip(self.dates, self.values))
    
class MetricResult:

    def __init__(self, name: str, value: int | float, date: date, is_list: bool = False):
        self.name = name
        self.value = value
        self.date = date
        self.is_list = is_list

class CommitResult:

    def __init__(self, hash: str, date: date):
        self.hash = hash
        self.date = date
        self.metric_results: list[MetricResult] = []

    def add_metric_result(self, metric_result: MetricResult):
        self.metric_results.append(metric_result)

class ProjectResult:

    def __init__(self, name: str = ''):
        self.name = name
        self.commit_results: list[CommitResult] = []

    def add_commit_result(self, commit_result: CommitResult):
        self.commit_results.append(commit_result)

    def metric_evolution(self, metric_name: str) -> MetricEvolution:    
        dates = self.compute_date_steps()
        values = []
        
        metric_results = sorted(self._metric_results(metric_name), key=lambda m: m.date, reverse=True)
        for date_step in dates:
            found_date = False
            for metric_result in metric_results:
                real_date = date(metric_result.date.year, metric_result.date.month, 1)
                if date_step >= real_date:
                    values.append(metric_result.value)
                    found_date = True
                    break
            # Fill the missing metric values, which may happen in categorical metrics
            if not found_date:
                values.append(0)
        
        assert len(dates) == len(values), f'{len(dates)} != {len(values)}'

        dates = DateUtils.formatted_dates(dates)
        return MetricEvolution(metric_name, dates, values)
    
    def compute_date_steps(self) -> list[date]:
        first_commit_date = self.commit_results[0].date
        last_commit_date = self.commit_results[-1].date
        # last_commit_date = date.today()
        return DateUtils.date_range(first_commit_date, last_commit_date)
    
    def _metric_results(self, metric_name: str) -> list[MetricResult]:
        metric_results = []
        for commit_result in self.commit_results:
            for metric_result in commit_result.metric_results:
                if metric_result.name == metric_name:
                    metric_results.append(metric_result)
        return metric_results

class GitEvoResult:

    def __init__(self, report_title: str, report_filename: str, date_unit: str, registered_metrics: list[MetricInfo]):
        self.report_title = report_title
        self.report_filename = report_filename
        self.registered_metrics = registered_metrics
        DateUtils.date_unit = date_unit

        self.project_result = None
        self._metric_data = MetricData()

    @property
    def metric_names(self) -> list[str]:
        return self._metric_data.names
    
    @property
    def metric_groups(self):
        return self._metric_data.groups_and_names
    
    @property
    def metric_dates(self) -> list[str]:
        date_steps = self.project_result.compute_date_steps()
        return DateUtils.formatted_dates(date_steps)
    
    @property
    def metric_version_chart_types(self) -> dict[str, str]:
        return {metric_info.group: metric_info.version_chart_type for metric_info in self.registered_metrics}
    
    @property
    def metric_show_version_charts(self) -> dict[str, bool]:
        return {metric_info.group: metric_info.show_version_chart for metric_info in self.registered_metrics} 
    
    @property
    def metric_tops_n(self) -> dict[str, str]:
        return {metric_info.group: metric_info.top_n for metric_info in self.registered_metrics}
    
    def add_metric_name(self, name: str):
        self._metric_data.add_metric_name(name)

    def add_metric_group(self, name: str | None, group: str):
        self._metric_data.add_metric_group(name, group)
    
    def metric_evolutions(self) -> list[MetricEvolution]:
        metric_evolutions = []
        for metric_name in self._metric_data.names:
            metric_evo = self.project_result.metric_evolution(metric_name)
            metric_evolutions.append(metric_evo)
        return metric_evolutions

class MetricData:

    def __init__(self):
        self._names = []
        self.groups_and_names: dict[str, set] = {}

    @property
    def names(self) -> list[str]:
        return list(dict.fromkeys(self._names))

    def add_metric_name(self, name: str):
        self._names.append(name)

    def add_metric_group(self, name: str | None, group: str):
        if name is None:
            self.groups_and_names[group] = set()
            return

        if group not in self.groups_and_names:
            self.groups_and_names[group] = {name}
        self.groups_and_names[group].add(name)