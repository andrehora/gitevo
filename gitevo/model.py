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

    def __init__(self, name: str):
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

    def __init__(self, report_title: str, report_filename: str, date_unit: str, 
                 registered_metrics: list[MetricInfo], last_version_only: bool):
        self.report_title = report_title
        self.report_filename = report_filename
        self.registered_metrics = registered_metrics
        self.last_version_only = last_version_only
        DateUtils.date_unit = date_unit

        self.project_results: list[ProjectResult] = []
        self._metrics_data = MetricData()

    @property
    def metric_names(self) -> list[str]:
        return self._metrics_data.names
    
    @property
    def metric_dates(self) -> list[str]:
        return DateUtils.formatted_dates(self._date_steps())
    
    @property
    def metric_groups(self):
        return self._metrics_data._groups_and_names
    
    @property
    def metric_version_chart_types(self) -> dict[str, str]:
        return {metric_info.group: metric_info.version_chart_type for metric_info in self.registered_metrics}
    
    @property
    def metric_show_version_charts(self) -> dict[str, bool]:
        return {metric_info.group: metric_info.show_version_chart for metric_info in self.registered_metrics} 
    
    @property
    def metric_tops_n(self) -> dict[str, str]:
        return {metric_info.group: metric_info.top_n for metric_info in self.registered_metrics}
    
    def add_metric_aggregate(self, name: str, aggregate: str):
        self._metrics_data.add_metric_aggregate(name, aggregate)

    def add_metric_group(self, name: str | None, group: str):
        self._metrics_data.add_metric_group(name, group)

    def add_project_result(self, project_result: ProjectResult):
        self.project_results.append(project_result)
    
    def metric_evolutions(self) -> list[MetricEvolution]:
        metric_evolutions = []
        for metric_name, metric_agg in self._metrics_data.names_and_aggregates:
            metric_evo = self._metric_evolution(metric_name, metric_agg)
            metric_evolutions.append(metric_evo)
        return metric_evolutions
    
    def _date_steps(self) -> list[date]:
        dates = set()
        for project_result in self.project_results:
            project_dates = project_result.compute_date_steps()
            dates.update(project_dates)
        return sorted(list(dates))

    def _metric_evolution(self, metric_name: str, aggregate: str) -> MetricEvolution:
        
        values_by_date = {date: [] for date in self.metric_dates}
        for project_result in self.project_results:
            metric_evolution = project_result.metric_evolution(metric_name)
            for date, value in metric_evolution.dates_and_values:

                if isinstance(value, list): values_by_date[date].extend(value)
                else: values_by_date[date].append(value)
        
        # Aggregate values
        values = []
        for metric_values in values_by_date.values():

            if not metric_values:
                values.append(0)
                continue
            
            value = None
            if aggregate in ['sum', 'max', 'min']:
                value = aggregate_basic(metric_values, aggregate)
            if aggregate in ['median', 'mean', 'mode']:
                value = aggregate_stat(metric_values, aggregate)
            
            assert value is not None
            values.append(value)

        return MetricEvolution(metric_name, self.metric_dates, values)

class MetricData:

    def __init__(self):
        self._names_and_aggregates: dict[str, str] = {}
        self._groups_and_names: dict[str, set] = {}

    @property
    def names(self) -> list[str]:
        return list(self._names_and_aggregates.keys())
    
    @property
    def names_and_aggregates(self):
        return self._names_and_aggregates.items()

    def add_metric_aggregate(self, name: str, aggregate: str):
        if name in self._names_and_aggregates:
            return
        self._names_and_aggregates[name] = aggregate

    def add_metric_group(self, name: str | None, group: str):
        if name is None:
            self._groups_and_names[group] = set()
            return

        if group not in self._groups_and_names:
            self._groups_and_names[group] = {name}
        self._groups_and_names[group].add(name)