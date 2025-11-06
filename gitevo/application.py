import os
import pathlib

from datetime import date, datetime
from collections import Counter

from tree_sitter import Node
from treeminer.repo import TreeMinerRepo, Commit
from treeminer.miners import BaseMiner

from gitevo.model import GitEvoResult, ProjectResult, CommitResult, MetricResult
from gitevo.info import MetricInfo
from gitevo.report_html import HtmlReport
from gitevo.report_csv import TableReport
from gitevo.utils import is_git_dir, stdout_msg, stdout_link, as_str, aggregate_stat, ensure_file_extension
from gitevo.exceptions import *

"""
This module contains the main GitEvo classes: GitEvo, ParsedCommit, and ParsedFile.
It provides functionality to analyze Git repositories, compute metrics, and generate reports.

See: https://github.com/andrehora/gitevo/tree/main/examples

Example:

    from gitevo import GitEvo, ParsedCommit

    git_url = 'https://github.com/pallets/flask'
    evo = GitEvo(repo=git_url, extension='.py')

    @evo.metric('Lines of code (LOC)')
    def loc(commit: ParsedCommit):
        return commit.loc

    @evo.metric('Python files')
    def python_files(commit: ParsedCommit):
        return len(commit.parsed_files)

    @evo.metric('Test files')
    def test_files(commit: ParsedCommit):
        test_files = [f for f in commit.parsed_files if 'test_' in f.name.lower()]
        return len(test_files)

    @evo.metric('LOC / Python files')
    def loc_per_file(commit: ParsedCommit):
        python_files = len(commit.parsed_files)
        if python_files == 0: return 0
        return commit.loc / python_files

    evo.run()

"""

class GitEvo:

    """
    GitEvo main class, the entrypoint to use GitEvo.

    Args:
        repo (str): Git repository URL or local path
        extension (str | None): File extension to analyze, eg, .py, .ts, .js, or .java
        from_year (int | None): Start year for analysis (default: current year - 5)
        to_year (int | None): End year for analysis (default: current year)
        date_unit (str): Date unit for analysis, either 'year' or 'month' (default: 'year')
        export_html (bool): Whether to export HTML report (default: True)
        export_csv (bool): Whether to export CSV report (default: True)
        report_filename (str | None): Custom report filename (default: None)
        report_title (str | None): Custom report title (default: None)
    Raises:
        BadGitRepo: If the repository is invalid
        BadDateUnit: If the date_unit is invalid
        BadYearRange: If from_year is greater than to_year
    """

    def __init__(self,
                *,
                repo: str,
                extension: str | None = None, 
                
                from_year: int | None = None,
                to_year: int | None = None,
                date_unit: str = 'year', 

                export_html: bool = True,
                export_csv: bool = True,
                report_filename: str | None = None,
                report_title: str | None = None):
        
        self.git_repos = self._ensure_git_repos(repo)
        
        if date_unit not in ['year', 'month']:
            raise BadDateUnit(f'date_unit must be year or month')
        
        if from_year is None:
            from_year = date.today().year - 5

        if to_year is None:
            to_year = date.today().year

        if from_year > to_year:
            raise BadYearRange(f'from_year must be equal or smaller than to_year')

        self.global_file_extension = ensure_file_extension(extension)
        self.date_unit = date_unit
        self.from_year = from_year
        self.to_year = to_year

        self.report_filename = report_filename
        if self.report_filename:
            self.report_filename = self.report_filename.strip()
        self.report_title = report_title
        if self.report_title:
            self.report_title = self.report_title.strip()
        
        self.export_html_report = export_html
        self.export_csv_report = export_csv

        self.registered_metrics: list[MetricInfo] = []
        self._analyzed_commits: list[str] = []

    # metric decorator
    def metric(self, name: str = None,
               *,
               extension: str | None = None, 
               categorical: bool = False, 
               group: str | None = None,
               version_chart_type: str = 'bar',
               show_version_chart: bool = True,
               top_n: int | None = None):
        
        def decorator(func):
            self.registered_metrics.append(
                MetricInfo(name=name, 
                           callback=func,
                           file_extension=ensure_file_extension(extension),
                           categorical=categorical,
                           group=group,
                           version_chart_type=version_chart_type,
                           show_version_chart=show_version_chart,
                           top_n=top_n))
            return func
        
        return decorator

    # def add_language(self, extension: str, tree_sitter_language: object):
    #     miner = GenericMiner
    #     miner.extension = extension
    #     miner.tree_sitter_language = tree_sitter_language
    #     self._repo.add_miner(miner)

    def run(self) -> GitEvoResult | list[GitEvoResult]:
        
        """
        Run GitEvo analysis on the provided repository or repositories.
        
        Returns:
            GitEvoResult | list[GitEvoResult]: The analysis result(s) for the repository or repositories.
        """

        print(f'Running GitEvo...')
        results = []
        for git_repo in self.git_repos:
            print('Processing repository:', git_repo)
            try:
                result = self._process_repository(git_repo)
                results.append(result)
            except (FileExtensionNotFound, BadReturnType, BadDateUnit, BadYearRange, BadLOCAggregate, BadVersionChart) as e:
                raise
            except Exception as e:
                print(f'Error processing {git_repo}: {e}')
                continue
        return results
    
    def _process_repository(self, git_repo: str) -> GitEvoResult:
        result = self._compute_metrics(git_repo)
        self._export_html(result)
        self._export_csv(result)
        return result
    
    def _compute_metrics(self, git_repo: str) -> GitEvoResult:

        mine_repo = TreeMinerRepo(git_repo)
        gitevo_result = GitEvoResult(self.report_title, self.report_filename, self.date_unit, self.registered_metrics)
        
        for metric_info in self.registered_metrics:
            # Sanity checks on registered_metrics
            self._check_registered_metrics(metric_info)
            if metric_info.file_extension is None:
                metric_info.file_extension = self.global_file_extension
            # Real names of the categorical metrics are known only at runtime, thus, now register None
            gitevo_result.add_metric_group(metric_info.name_or_none_for_categorical, metric_info.group)

        project_result = ProjectResult()
        gitevo_result.project_result = project_result

        project_name = None
        project_commits = set()

        for commit in mine_repo.commits:

            if project_name is None:
                project_name = commit.project_name
                project_result.name = project_name

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

            # Chache parsed commits for each file extension, eg, .py, .js, .java, etc
            parsed_commits = _ParsedCommitCache(commit, self._all_file_extensions())
            print(f'- Date: {selected_date}, commit: {commit.hash[0:10]}, files: {parsed_commits.file_stats()}')

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

                    for real_name, value in Counter(metric_value).most_common():
                        assert isinstance(real_name, str), f'categorical metric {metric_info.name} should return list[str]'
                        metric_result = MetricResult(name=real_name, value=value, date=commit_result.date)
                        commit_result.add_metric_result(metric_result)
                        
                        # Register the real name of the categorical metric
                        gitevo_result.add_metric_name(real_name)
                        gitevo_result.add_metric_group(real_name, metric_info.group)
                
                # Process numerical metrics
                else:

                    if not isinstance(metric_value, (int, float)):
                        raise BadReturnType(f'numerical metric {metric_info.name} should return int or float')

                    metric_result = MetricResult(name=metric_info.name, value=metric_value, date=commit_result.date)
                    commit_result.add_metric_result(metric_result)
                    gitevo_result.add_metric_name(metric_info.name)

            project_result.add_commit_result(commit_result)
        
        return gitevo_result
    
    def _ensure_git_repos(self, repo: str) -> list[str]:

        if not repo or repo is None:
            raise BadGitRepo('Invalid repository')

        # repo is str
        if isinstance(repo, str):
            # repo is remote
            if self._is_git_remote(repo):
                # print('Git URL:', repo)
                return [repo]
            else:
                # repo is local dir
                if not os.path.isdir(repo):
                    raise BadGitRepo(f'{repo} is not a directory')
                
                # Check if repo is a git dir
                if is_git_dir(repo):
                    # print('Local Git repository:', repo)
                    return [repo]

                # Check if repo is a dir with git projects
                paths = self._projects_dir(repo)
                if not paths:
                    raise BadGitRepo(f'{repo} is not a directory with git repositories')
                git_repos = []
                print('Directory containing multiple projects:', repo)
                for path in paths:
                    if is_git_dir(path):
                        print('- Found Git repository:', path)
                        git_repos.append(path)
                    else:
                        print('- Not a Git repository:', path)
                return git_repos
        
        raise BadGitRepo('Invalid repository')
    
    def _check_registered_metrics(self, metric_info: MetricInfo):
        
        if self.global_file_extension is None and metric_info.file_extension is None:
            raise FileExtensionNotFound(f'extension should be defined globally or in metric {metric_info.name}')
            
        if metric_info.version_chart_type not in ['donut', 'pie', 'bar', 'hbar']:
            raise BadVersionChart(f'version chart in {metric_info.name} should be donut, pie, bar, or hbar, not {metric_info.version_chart_type}')
    
    def _is_git_remote(self, repo: str) -> bool:
        return repo.startswith(("git@", "https://", "http://", "git://"))
    
    def _projects_dir(self, folder_path: str):
        return [str(d.resolve()) for d in pathlib.Path(folder_path).iterdir() if d.is_dir()]
    
    def _write_msg(self, format: str, path: str) -> str:
        link = stdout_link(path, f'file://{path}')
        msg =  f'{format} report: {link}'
        return stdout_msg(msg)
            
    def _all_file_extensions(self) -> set[str]:
        return set([metric_info.file_extension for metric_info in self.registered_metrics])
    
    def _export_html(self, result: GitEvoResult):
        if not self.export_html_report:
            return
        path = HtmlReport(result).export_html()
        print(self._write_msg('HTML', path))

    def _export_csv(self, result: GitEvoResult):
        if not self.export_csv_report:
            return
        path = TableReport(result).export_csv()
        print(self._write_msg('CSV', path))
    
class ParsedFile:

    """
    Represents a parsed file in a commit, containing its name, path, tree-sitter nodes, and lines of code (LOC).
    """

    def __init__(self, name: str, path: str, nodes: list[Node], loc: int):
        self.name = name
        self.path = path
        self.nodes = nodes
        self.loc = loc
    
class ParsedCommit:

    """
    Represents a parsed commit in a repository, containing its hash, date, file extension, parsed files,
    tree-sitter nodes, and lines of code (LOC).
    """

    def __init__(self, hash: str, date: datetime, file_extension: str, parsed_files: list[ParsedFile]):
        self.hash = hash
        self.date = date
        self.file_extension = file_extension
        self._parsed_files = parsed_files
        self._nodes = None
        self._loc = None

    @property
    def parsed_files(self) -> list[ParsedFile]:
        """
        Returns the list of parsed files in the commit.
        Returns:
            list[ParsedFile]: The list of parsed files.
        """
        return self._parsed_files

    @property
    def nodes(self) -> list[Node]:
        """
        Returns the list of tree-sitter nodes in the commit.
        Returns:
            list[Node]: The list of nodes.
        """
        if self._nodes is None:
            self._nodes = [node for file in self.parsed_files for node in file.nodes]
        return self._nodes
    
    @property
    def loc(self) -> int:
        """
        Returns the total lines of code (LOC) in the commit.
        Returns:
            int: The total LOC.
        """
        if self._loc is None:
            self._loc = sum([file.loc for file in self.parsed_files])
        return self._loc

    def count_nodes(self, node_types: str | list[str] | None = None) -> int:
        """
        Counts the number of tree-sitter nodes in the commit, optionally filtered by node types.

        See node types examples at:
        https://github.com/tree-sitter/tree-sitter-python/blob/master/src/node-types.json
        https://github.com/tree-sitter/tree-sitter-javascript/blob/master/src/node-types.json
        https://github.com/tree-sitter/tree-sitter-typescript/blob/master/typescript/src/node-types.json
        https://github.com/tree-sitter/tree-sitter-java/blob/master/src/node-types.json

        Returns:
            int: The count of nodes.
        """
        if node_types is None:
            return len(self.nodes)
        return len(self.find_nodes_by_type(node_types))

    def loc_by_type(self, node_type: str, aggregate: str = 'median') -> int | float:
        """
        Calculates the lines of code (LOC) for nodes of a specific type, using the specified aggregation method.
        Args:
            node_type (str): The type of node to calculate LOC for.
            aggregate (str): The aggregation method to use ('median', 'mean', 'mode').
        Returns:
            int | float: The aggregated LOC value.
        Raises:
            BadLOCAggregate: If the aggregate method is invalid.
        """
        if aggregate is not None and aggregate not in ['median', 'mean', 'mode']:
            raise BadLOCAggregate(f'LOC aggregate should be median, mean, or mode')
        
        nodes = self.find_nodes_by_type([node_type])
        if not nodes:
            return 0

        locs = [len(as_str(node.text).split('\n')) for node in nodes]
        return aggregate_stat(locs, aggregate)
    
    def find_node_types(self, node_types: str | list[str] = None) -> list[str]:
        """
        Finds the types of tree-sitter nodes in the commit, optionally filtered by node types.
        Args:
            node_types (str | list[str], optional): The node types to filter by.
        Returns:
            list[str]: The list of node types.
        """
        if node_types is None:
            return [node.type for node in self.nodes]

        if isinstance(node_types, str):
            node_types = [node_types]    
    
        return [node.type for node in self.nodes if node.type in node_types]
    
    def find_nodes_by_type(self, node_types: str | list[str]) -> list[Node]:
        """
        Finds the tree-sitter nodes in the commit by their types.
        Args:
            node_types (str | list[str]): The node types to filter by.
        Returns:
            list[Node]: The list of nodes.
        """
        if isinstance(node_types, str):
            node_types = [node_types]

        return [node for node in self.nodes if node.type in node_types]
    
    def named_children_for(self, node: Node) -> list[Node]:
        """
        Returns the named children of a given tree-sitter node.
        Args:
            node (Node): The tree-sitter node.
        Returns:
            list[Node]: The list of named child nodes.
        """
        return [each for each in node.children if each.is_named]
    
    def descendant_nodes_for(self, node: Node) -> list[Node]:
        """
        Returns the descendant nodes of a given tree-sitter node.
        Args:
            node (Node): The tree-sitter node.
        Returns:
            list[Node]: The list of descendant nodes.
        """
        descendants = []
        def traverse_node(current_node):
            descendants.append(current_node)
            for child in current_node.children:
                traverse_node(child)

        traverse_node(node)
        return descendants
    
    def descendant_node_by_field_name(self, node: Node, name: str) -> Node | None:
        """
        Finds a descendant node of a given tree-sitter node by its field name.
        Args:
            node (Node): The tree-sitter node.
            name (str): The field name to search for.
        Returns:
            Node | None: The descendant node with the specified field name, or None if not found.
        """
        for desc_node in self.descendant_nodes_for(node):
            target_node = desc_node.child_by_field_name(name)
            if target_node is not None:
                return target_node
        return None

class _ParsedCommitCache:

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
    
class GenericMiner(BaseMiner):
    extension: str = None
    tree_sitter_language: object = None