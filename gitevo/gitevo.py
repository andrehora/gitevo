import os
import statistics
import json
import pathlib
import sys

from datetime import date, datetime
from collections import Counter

from tree_sitter import Node
from git.repo.fun import is_git_dir
from treeminer.repo import TreeMinerRepo, Commit
from treeminer.miners import BaseMiner

def stdout_link(text: str, url: str) -> str:
    # from coverage.py
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        return f"\033]8;;{url}\a{text}\033]8;;\a"
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
    

class GenericMiner(BaseMiner):
    extension: str = None
    tree_sitter_language: object = None


class MetricInfo:
    
    def __init__(self, name: str, callback, file_extension: str, categorical: bool,
                 aggregate: str, group: str, version_chart_type: str, show_version_chart: bool,
                 top_n: int):
        
        self._name = name
        self.callback = callback
        self.file_extension = file_extension
        self.categorical = categorical
        self.aggregate = aggregate
        self._group = group
        self.version_chart_type = version_chart_type
        self.show_version_chart = show_version_chart
        self.top_n = top_n

    @property
    def name(self) -> str:
        if self._name is None:
            return self.callback.__name__
        return self._name.strip()
    
    @property
    def name_or_none_for_categorical(self) -> str | None:
        if self.categorical:
            return None
        return self.name
    
    @property
    def group(self) -> str:
        if self._group is None:
            return self.name
        return self._group.strip()
    
class BeforeCommitInfo:

    def __init__(self, file_extension: str, callback: callable):
        self.file_extension = file_extension
        self.callback = callback
    
class ParsedFile:

    def __init__(self, name: str, path: str, nodes: list[Node], loc: int):
        self.name = name
        self.path = path
        self.nodes = nodes
        self.loc = loc

class ParsedCommit:
    
    def __init__(self, hash: str, date: datetime, file_extension: str, parsed_files: list[ParsedFile]):
        self.hash = hash
        self.date = date
        self.file_extension = file_extension
        self.parsed_files = parsed_files
        self._nodes = None
        self._loc = None

    @property
    def nodes(self) -> list[Node]:
        if self._nodes is None:
            self._nodes = [node for file in self.parsed_files for node in file.nodes]
        return self._nodes
    
    @property
    def loc(self) -> int:
        if self._loc is None:
            self._loc = sum([file.loc for file in self.parsed_files])
        return self._loc
    
    def node_types(self, node_types: list[str] = None) -> list[str]:
        if node_types is None:
            return [node.type for node in self.nodes]
        return [node.type for node in self.nodes if node.type in node_types]
    
    def count_nodes(self, node_types: list[str] = None) -> int:
        if node_types is None:
            return len(self.nodes)
        return len(self.find_nodes_by_type(node_types))
    
    def loc_for(self, node_type: str, aggregate: str | None = None) -> int | float | list[int]:

        if aggregate is not None and aggregate not in ['median', 'mean', 'mode']:
            raise BadLOCAggregate(f'LOC aggregate should be median, mean, or mode')
        
        nodes = self.find_nodes_by_type([node_type])

        if not nodes:
            return []

        locs = [len(as_str(node.text).split('\n')) for node in nodes]
        if aggregate is None:
            return locs
        
        return aggregate_stat(locs, aggregate)
    
    def find_nodes_by_type(self, node_types: list[str]) -> list[Node]:
        return [node for node in self.nodes if node.type in node_types]
    
    def named_children(self, node: Node) -> list[Node]:
        return [each for each in node.children if each.is_named]
    
    def descendant_nodes(self, node: Node) -> list[Node]:
        descendants = []
        def traverse_node(current_node):
            descendants.append(current_node)
            for child in current_node.children:
                traverse_node(child)

        traverse_node(node)
        return descendants
    
    def descendant_node_by_field_name(self, node: Node, name: str) -> Node | None:
        for desc_node in self.descendant_nodes(node):
            target_node = desc_node.child_by_field_name(name)
            if target_node is not None:
                return target_node
        return None


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
    
    def __str__(self):
        return f'{self.name} {str(self.values)}'
    
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
        dates = self.date_steps()
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
    
    def date_steps(self) -> list[date]:
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

    def __init__(self, title: str, html_filename: str, date_unit: str, registered_metrics: list[MetricInfo], last_version_only: bool):
        self.title = title
        self.html_filename = html_filename
        self.registered_metrics = registered_metrics
        self.last_version_only = last_version_only
        DateUtils.date_unit = date_unit

        self.project_results: list[ProjectResult] = []
        self._metrics_data = MetricsData()

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
    
    def as_html(self):
        return HtmlReport(self).generate_html()

    def as_table(self):
        return TableReport(self).generate_table()
    
    def _date_steps(self) -> list[date]:
        dates = set()
        for project_result in self.project_results:
            project_dates = project_result.date_steps()
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

class MetricsData:

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
                
class GitEvo:

    def __init__(self,
                *,
                repo: str | list[str],
                extension: str | None = None, 
                date_unit: str = 'year', 
                from_year: int | None = None,
                to_year: int | None = None,
                title: str = 'GitEvo',
                html_filename: str = 'index.html',
                last_version_only: bool = False):
                        
        self.project_repos = self._check_valid_git_projects(repo)
        
        if date_unit not in ['year', 'month']:
            raise BadDateUnit(f'date_unit must be year or month')
        
        if from_year is None:
            from_year = date.today().year - 5

        if to_year is None:
            to_year = date.today().year

        if from_year > to_year:
            raise BadYearRange(f'from_year must be equal or smaller than to_year')

        self.global_file_extension = extension
        self.date_unit = date_unit
        self.from_year = from_year
        self.to_year = to_year
        self.title = title.strip()
        self.html_filename = html_filename.strip()
        self.last_version_only = last_version_only

        self.registered_metrics: list[MetricInfo] = []
        self.registered_before_commits: list[BeforeCommitInfo] = []

        self._analyzed_commits: list[str] = []
        self._repo = TreeMinerRepo(self.project_repos)

    def add_language(self, extension: str, tree_sitter_language: object):
        miner = GenericMiner
        miner.extension = extension
        miner.tree_sitter_language = tree_sitter_language
        self._repo.add_miner(miner)

    def _check_valid_git_projects(self, repo: str | list[str]) -> str | list[str]:

        if not repo or repo is None:
            raise BadGitRepo('Invalid repository')

        # project_path is str
        if isinstance(repo, str):
            # Project_path is remote
            if self._is_git_remote(repo):
                return repo
            else:
                # Project_path is local dir

                if not os.path.isdir(repo):
                    raise BadGitRepo(f'{repo} is not a directory')
                
                # Check if project_path is a git dir
                if self._is_git_dir(repo):
                    return repo

                # Check if project_path is a dir with git projects
                paths = self._projects_dir(repo)
                if not paths:
                    raise BadGitRepo(f'{repo} is not a directory with git repositories')
                for path in paths:
                    if not self._is_git_dir(path):
                        raise BadGitRepo(f'{path} is not a git repository')
                return paths
        
        # project_path is list
        if isinstance(repo, list):
            for path in repo:
                if not self._is_git_remote(path) and not self._is_git_dir(path):
                    raise BadGitRepo(f'{path} is not a git repository')
            return repo
        
        raise BadGitRepo('Invalid repository')
    
    def _is_git_dir(self, project_path):
        git_path = os.path.join(project_path, '.git')
        return is_git_dir(git_path)
    
    def _is_git_remote(self, repo: str) -> bool:
        return repo.startswith(("git@", "https://", "http://", "git://"))
    
    def _projects_dir(self, folder_path: str):
        return [str(d.resolve()) for d in pathlib.Path(folder_path).iterdir() if d.is_dir()]

    def metric(self, name: str = None,
               *,
               extension: str | None = None, 
               categorical: bool = False, 
               aggregate: str = 'sum',
               group: str | None = None,
               version_chart_type: str = 'bar',
               show_version_chart: bool = True,
               top_n: int | None = None):
        
        def decorator(func):
            self.registered_metrics.append(
                MetricInfo(name=name, 
                           callback=func,
                           file_extension=extension,
                           categorical=categorical,
                           aggregate=aggregate,
                           group=group,
                           version_chart_type=version_chart_type,
                           show_version_chart=show_version_chart,
                           top_n=top_n))
            return func
        
        return decorator
    
    def before(self, file_extension: str | None = None):

        def decorator(func):
            self.registered_before_commits.append(
                BeforeCommitInfo(file_extension, callback=func,))    
            return func
        
        return decorator
    
    def run(self) -> GitEvoResult:
        print(f'Running GitEvo...')
        result = self._compute_metrics()
        html_path = result.as_html()
        html_link = stdout_link(html_path, f'file://{html_path}')
        print(f'Wrote HTML report to {html_link}')
        return result
    
    def _compute_metrics(self) -> GitEvoResult:

        # Sanity checks on registered_metrics
        result = GitEvoResult(self.title, self.html_filename, self.date_unit, self.registered_metrics, self.last_version_only)
        for metric_info in self.registered_metrics:

            if self.global_file_extension is None and metric_info.file_extension is None:
                raise FileExtensionNotFound(f'file_extension should be defined globally or in metric {metric_info.name}')
            
            if metric_info.aggregate not in ['median', 'mean', 'mode', 'sum', 'max', 'min']:
                raise BadAggregate(f'aggregate in metric {metric_info.name} should be median, mean, mode, sum, max, or min, not {metric_info.aggregate}')
            
            if metric_info.version_chart_type not in ['donut', 'pie', 'bar', 'hbar']:
                raise BadVersionChart(f'version chart in {metric_info.name} should be donut, pie, bar, or hbar, not {metric_info.version_chart_type}')
            
            if metric_info.file_extension is None:
                metric_info.file_extension = self.global_file_extension
            
            # Real names of the categorical metrics are known only at runtime, thus, now register None
            result.add_metric_group(metric_info.name_or_none_for_categorical, metric_info.group)
                
        project_result = None
        project_name = ''
        project_commits = set()

        last_commit_hash = None
        if self.last_version_only:
            last_commit_hash = self._repo.lastest_commit.hash

        for commit in self._repo.commits:
            
            # Create new project result if new project name
            if project_name != commit.project_name:
                print(f'{commit.project_name}')
                project_name = commit.project_name
                project_commits = set()
                project_result = ProjectResult(commit.project_name)
                result.add_project_result(project_result)

            if not self.last_version_only:
                # Skip commit based on from and to year 
                if commit.committer_date.year < self.from_year:
                    continue
                if commit.committer_date.year > self.to_year:
                    continue
                
                # Skip commit if year or month is already analyzed
                commit_year = commit.committer_date.year
                selected_date = (commit_year, commit.committer_date.month) if self.date_unit == 'month' else commit_year
                if selected_date in project_commits:
                    continue

                project_commits.add(selected_date)
            else:
                # Skip commit based on last_commit_hash
                if last_commit_hash != commit.hash:
                    continue
                selected_date = commit.committer_date

            # Chache parsed commits for each file extension, eg, .py, .js, .java, etc
            parsed_commits = ParsedCommits(commit, self._all_file_extensions())
            print(f'- Date: {selected_date}, commit: {commit.hash[0:10]}, files: {parsed_commits.file_stats()}')
            
            # Iterate on the before commit
            for before_commit_info in self.registered_before_commits:
                file_extension = before_commit_info.file_extension
                # Get parsed_commit, run the before commit callback, and update parsed_commits
                parsed_commit = parsed_commits.get_parsed_commit_for(file_extension)
                new_parsed_commit = before_commit_info.callback(parsed_commit)
                parsed_commits.update_parsed_commit_for(file_extension, new_parsed_commit)

            # Iterate on each metric
            commit_result = CommitResult(commit.hash, commit.committer_date.date())
            for metric_info in self.registered_metrics:
                
                # Get parsed_commit and run the metric callback
                parsed_commit = parsed_commits.get_parsed_commit_for(metric_info.file_extension)
                metric_value = metric_info.callback(parsed_commit)

                # Process categorical metrics
                if metric_info.categorical: 

                    if not isinstance(metric_value, list):
                        raise BadReturnType(f'categorical metric {metric_info.name} should return list[str]')

                    if not metric_value:
                        continue
                        # raise BadReturnType(f'categorical metric {metric_info.name} should return list[str], not an empty list')

                    for real_name, value in Counter(metric_value).most_common():
                        assert isinstance(real_name, str), f'categorical metric {metric_info.name} should return return list[str]'
                        metric_result = MetricResult(name=real_name, value=value, date=commit_result.date)
                        commit_result.add_metric_result(metric_result)
                        
                        # Register the real name of the categorical metric
                        result.add_metric_group(real_name, metric_info.group)
                        result.add_metric_aggregate(real_name, metric_info.aggregate)
                
                # Process numerical metrics
                else:

                    if not isinstance(metric_value, (int, float, list)):
                        raise BadReturnType(f'numerical metric {metric_info.name} should return int, float, or list[int|float]')

                    metric_result = MetricResult(name=metric_info.name, value=metric_value, date=commit_result.date)
                    commit_result.add_metric_result(metric_result)
                    result.add_metric_aggregate(metric_info.name, metric_info.aggregate)

            project_result.add_commit_result(commit_result)
        
        return result
            
    def _all_file_extensions(self) -> set[str]:
        return set([metric_info.file_extension for metric_info in self.registered_metrics])

    
class ParsedCommits:

    def __init__(self, commit: Commit, file_extensions: list[str]):
        self.commit = commit
        self.file_extensions = file_extensions
        
        self._parsed_commits: dict[str, ParsedCommit] = {}
        self._create_parsed_commits()

    def get_parsed_commit_for(self, file_extension: str) -> ParsedCommit:
        assert file_extension in self.file_extensions, f'{file_extension} not in {self.file_extensions})'
        return self._parsed_commits[file_extension]
    
    def update_parsed_commit_for(self, file_extension: str, parsed_commit: ParsedCommit):
        self._parsed_commits[file_extension] = parsed_commit

    def file_stats(self):
        file_stats = [f'{extension} {len(pc.parsed_files)}' for extension, pc in self._parsed_commits.items()]
        return ' '.join(file_stats)
    
    def _create_parsed_commits(self):
        for file_extension in self.file_extensions:
            self._parsed_commits[file_extension] = self._create_parsed_commit(file_extension)

    def _create_parsed_commit(self, file_extension: str) -> ParsedCommit:
        parsed_files = []
        for file in self.commit.all_files([file_extension]):
            file_nodes = [node for node in file.tree_nodes]
            parsed_file = ParsedFile(file.filename, file.path, file_nodes, file.loc)
            parsed_files.append(parsed_file)
        return ParsedCommit(self.commit.hash, self.commit.committer_date, file_extension, parsed_files)
    
class FileExtensionNotFound(Exception):
    pass

class BadAggregate(Exception):
    pass

class BadReturnType(Exception):
    pass

class BadDateUnit(Exception):
    pass

class BadLOCAggregate(Exception):
    pass

class BadGitRepo(Exception):
    pass

class BadVersionChart(Exception):
    pass

class BadYearRange(Exception):
    pass

class TableReport:

    DATE_COLUMN_NAME = 'date'
    
    def __init__(self, result: GitEvoResult):
        self.metric_names = result.metric_names
        self.metric_dates = result.metric_dates
        self.evolutions = result.metric_evolutions()
    
    def generate_table(self) -> list[list[str]]:
        header = self._header()
        t_values = self.transpose_matrix(self._values())
        assert len(header) == len(t_values[0])
        t_values.insert(0, header)
        return t_values
    
    def generate_table2(self) -> list[list[str]]:
        return self.transpose_matrix(self.generate_table())

    def transpose_matrix(self, matrix: list[list]) -> list[list]:
        return [list(row) for row in zip(*matrix)]
    
    def _header(self) -> list[str]:
        return [self.DATE_COLUMN_NAME] + self.metric_names
    
    def _values(self) -> list[list[str]]:
        values = [evo.values_as_str for evo in self.evolutions]
        values.insert(0, self.metric_dates)
        return values
    
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


class HtmlReport:

    TEMPLATE_HTML_FILENAME = 'template.html'
    JSON_DATA_PLACEHOLDER = '{{JSON_DATA}}'
    TITLE_PLACEHOLDER = '{{TITLE}}'
    CREATED_DATE_PLACEHOLDER = '{{CREATED_DATE}}'

    def __init__(self, result: GitEvoResult):
        self.title = result.title
        self.html_filename = result.html_filename
        self.metric_dates = result.metric_dates
        self.metric_groups = result.metric_groups
        self.metric_version_chart_types = result.metric_version_chart_types
        self.metric_show_version_charts = result.metric_show_version_charts
        self.metric_tops_n = result.metric_tops_n
        self.metric_evolutions = result.metric_evolutions()
        self.last_version_only = result.last_version_only

    def generate_html(self) -> str:
        json_data = self._json_data()
        template = self._read_template()
        content = self._replace_json_data(template, json_data)
        content = self._replace_title(content, self.title)
        content = self._replace_created_date(content)
        self._write_html(content)
        return os.path.join(os.getcwd(), self.html_filename)

    def _json_data(self):
        return self._build_charts()

    def _build_charts(self) -> list[dict]:
        charts = []
        print('Exported charts:')
        for group_name, metric_names in self.metric_groups.items():
            assert group_name in self.metric_tops_n
            
            group_evolution = self._find_metric_evolutions(metric_names)
            if not group_evolution:
                print(f'- Empty data (chart is omitted): {group_name}')
                continue

            top_n = self.metric_tops_n[group_name]
            
            # Build chart
            evo_chart = Chart(group_name, self.metric_dates, group_evolution, top_n)
            evo_msg, version_msg = '', ''

            if len(self.metric_dates) >= 2 and not self.last_version_only:
                charts.append(evo_chart.evo_dict())
                evo_msg = 'evolution'

            # Build last version chart
            assert group_name in self.metric_version_chart_types
            assert group_name in self.metric_show_version_charts
            
            version_chart_type = self.metric_version_chart_types[group_name]
            show_version_chart = self.metric_show_version_charts[group_name]
            if show_version_chart:
                charts.append(evo_chart.version_dict(version_chart_type))
                version_msg = 'version'
            
            if evo_msg and version_msg: msg = f'{evo_msg} and {version_msg} charts'
            elif evo_msg: msg = f'{evo_msg} chart'
            elif version_msg: msg = f'{version_msg} chart'
            else: msg = 'no chart'
            print(f'- OK: {group_name} -> {msg}')

        return charts
            
    def _find_metric_evolutions(self, metric_names):
        return [evolution for evolution in self.metric_evolutions if evolution.name in metric_names]
    
    def _read_template(self):
        with open(self.TEMPLATE_HTML_FILENAME, 'r') as template_file:
            template = template_file.read()
        return template

    def _write_html(self, html_content):
        with open(self.html_filename, 'w') as output_file:
            output_file.write(html_content)

    def _replace_json_data(self, source, json_data):
        return source.replace(self.JSON_DATA_PLACEHOLDER, json.dumps(json_data, indent=3))

    def _replace_title(self, source, content):
        return source.replace(self.TITLE_PLACEHOLDER, content)

    def _replace_created_date(self, source):
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        return source.replace(self.CREATED_DATE_PLACEHOLDER, now)
