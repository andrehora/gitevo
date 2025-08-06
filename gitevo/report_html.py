import os
import json

from datetime import datetime
from gitevo.model import GitEvoResult, MetricEvolution


class HtmlReport:

    TEMPLATE_HTML_FILENAME = 'template.html'
    JSON_DATA_PLACEHOLDER = '{{JSON_DATA}}'
    TITLE_PLACEHOLDER = '{{TITLE}}'
    CREATED_DATE_PLACEHOLDER = '{{CREATED_DATE}}'

    def __init__(self, result: GitEvoResult):

        self.report_filename = self._ensure_filename(result)
        self.report_title = self._ensure_title(result)

        self.metric_dates = result.metric_dates
        self.metric_groups = result.metric_groups
        self.metric_version_chart_types = result.metric_version_chart_types
        self.metric_show_version_charts = result.metric_show_version_charts
        self.metric_tops_n = result.metric_tops_n
        self.metric_evolutions = result.metric_evolutions()

    def export_html(self) -> str:
        json_data = self._json_data()
        template = self._read_template()
        content = self._replace_json_data(template, json_data)
        content = self._replace_title(content, self.report_title)
        content = self._replace_created_date(content)
        self._write_html(content)
        return os.path.join(os.getcwd(), self.report_filename)
    
    def _ensure_filename(self, result: GitEvoResult) -> str:
        if result.report_filename is None:
            filename = f'report_{result.project_result.name}.html'
            return filename
        return f'{result.report_filename}.html'
    
    def _ensure_title(self, result: GitEvoResult) -> str:
        if result.report_title is None:
            return result.project_result.name
        return result.report_title

    def _json_data(self):
        return self._build_charts()

    def _build_charts(self) -> list[dict]:
        charts = []
        cont = 0
        for group_name, metric_names in self.metric_groups.items():
            assert group_name in self.metric_tops_n
            cont += 1
            
            group_evolution = self._find_metric_evolutions(metric_names)
            if not group_evolution:
                continue

            top_n = self.metric_tops_n[group_name]
            
            # Build chart
            evo_chart = Chart(group_name, self.metric_dates, group_evolution, top_n)

            # Build last version chart
            assert group_name in self.metric_version_chart_types
            assert group_name in self.metric_show_version_charts
            
            version_chart_type = self.metric_version_chart_types[group_name]
            show_version_chart = self.metric_show_version_charts[group_name]
            if show_version_chart:
                charts.append(evo_chart.version_dict(version_chart_type))

            # Build evolution chart
            if len(self.metric_dates) >= 2:
                charts.append(evo_chart.evo_dict())

        return charts
            
    def _find_metric_evolutions(self, metric_names):
        return [evolution for evolution in self.metric_evolutions if evolution.name in metric_names]
    
    def _read_template(self):
        absolute_template_filename = self._absolute_filename(self.TEMPLATE_HTML_FILENAME)
        with open(absolute_template_filename, 'r') as template_file:
            template = template_file.read()
        return template

    def _write_html(self, html_content):
        with open(self.report_filename, 'w') as output_file:
            output_file.write(html_content)

    def _replace_json_data(self, source, json_data):
        return source.replace(self.JSON_DATA_PLACEHOLDER, json.dumps(json_data, indent=3))

    def _replace_title(self, source, content):
        return source.replace(self.TITLE_PLACEHOLDER, content)

    def _replace_created_date(self, source):
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        return source.replace(self.CREATED_DATE_PLACEHOLDER, now)
    
    def _absolute_filename(self, filename: str):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, filename)


class Chart:

    border_colors = ["#36A2EB80", "#FF638480", "#FF9F4080", "#FFCE5680", "#4BC0C080", "#9966FF80", "#C9CBCF80"]
    background_colors = ["#36A2EB", "#FF6384", "#FF9F40", "#FFCE56", "#4BC0C0", "#9966FF", "#C9CBCF"]

    def __init__(self, title: str, metric_dates: list[str], group_evolution: list[MetricEvolution], top_n: int):
        
        self.title = title
        self.metric_dates = metric_dates

        self.group_evolution = sorted(group_evolution, key=lambda metric: metric.values[-1], reverse=True)
        if top_n is not None:
            self.group_evolution = self.group_evolution[0:top_n]

    @property
    def is_single_metric(self):
        return len(self.group_evolution) == 1
    
    @property
    def is_multi_metrics(self):
        return not self.is_single_metric
        
    def evo_dict(self) -> dict:
        return {
            'title': self.title,
            'type': 'line',
            'indexAxis': 'x',
            'display_legend': self.is_multi_metrics,
            'labels': self.metric_dates,
            'datasets': self._evo_datasets()
        }
    
    def version_dict(self, chart_type: str) -> dict:

        lastest_date = self.metric_dates[-1]
        title = f'{self.title} - {lastest_date}'
        indexAxis = 'x'

        # doughnut is the actual name is Chart.js
        if chart_type == 'donut':
            chart_type = 'doughnut'
        
        # hbar is simply a bar chart with indexAxis y
        if chart_type == 'hbar':
            chart_type = 'bar'
            indexAxis = 'y'

        # no need to display legend in bar and hbar charts
        display_legend = False if chart_type in ['bar', 'hbar'] else True
        version_labels = [metric.name for metric in self.group_evolution]
        
        return {
            'title': title,
            'indexAxis': indexAxis,
            'type': chart_type,
            'display_legend': display_legend,
            'labels': version_labels,
            'datasets': self._version_dataset()
        }
    
    def _evo_datasets(self) -> list:

        if self.is_single_metric:
            return [{'data': self.group_evolution[0].values}]
        
        return [{'label': metric.name, 
                 'data': metric.values} for metric in self.group_evolution]
    
    def _version_dataset(self) -> list:
        # Get the most recent metric values (this year) 
        values = [metric.values[-1] for metric in self.group_evolution]
        
        return [{'data': values,
                 'backgroundColor': self.background_colors}]