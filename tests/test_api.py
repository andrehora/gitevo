import pytest

from datetime import date
from git import Repo
from gitevo import GitEvo, ParsedCommit
from gitevo.exceptions import BadReturnType, BadAggregate, BadLOCAggregate, FileExtensionNotFound


def test_register_single_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('Single metric')
    def single_metric(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)
    assert result.registered_metrics[0].name == 'Single metric'

    assert len(result.registered_metrics) == 1
    assert result.registered_metrics[0].name == 'Single metric'
    assert result.registered_metrics[0].group == 'Single metric'
    assert result.registered_metrics[0].file_extension == '.py'
    assert result.registered_metrics[0].callback == single_metric

def test_register_multiple_metrics(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('Metric 1')
    def m1(commit: ParsedCommit):
        return 1

    @evo.metric('Metric 2')
    def m2(commit: ParsedCommit):
        return 2

    result = evo.run(html=False)

    assert len(result.registered_metrics) == 2

    assert result.registered_metrics[0].name == 'Metric 1'
    assert result.registered_metrics[0].group == 'Metric 1'
    assert result.registered_metrics[0].file_extension == '.py'
    assert result.registered_metrics[0].callback == m1

    assert result.registered_metrics[1].name == 'Metric 2'
    assert result.registered_metrics[1].group == 'Metric 2'
    assert result.registered_metrics[1].file_extension == '.py'
    assert result.registered_metrics[1].callback == m2

def test_register_no_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')
    result = evo.run(html=False)
    assert len(result.registered_metrics) == 0

def test_register_unamed_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric()
    def my_metric_name(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)
    assert result.registered_metrics[0].name == 'my_metric_name'
    assert result.registered_metrics[0].group == 'my_metric_name'

def test_register_before(local_repo):

    class MyData:
        def __init__(self, commit):
            self.commit = commit
            self.value = 100

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.before(file_extension='.py')
    def before(commit: ParsedCommit):
        return MyData(commit)

    @evo.metric('m1')
    def m1(my_data: MyData):
        return my_data.value
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [100, 100, 100, 100, 100, 100]

def test_commit_metadata_by_year(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='year')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert len(result.project_results) == 1

    project_result = result.project_results[0]
    assert project_result.name == 'testrepo'
    assert len(project_result.commit_results) >= 4

    commit_result = project_result.commit_results[0]
    assert commit_result.hash == '57a6ac0058bef51f396a4322c38db69d5c26c4ff'
    assert commit_result.date == date(2020, 1, 1)

    commit_result = project_result.commit_results[1]
    assert commit_result.hash == '93d736df57207320363124123487467ffdfa5122'
    assert commit_result.date == date(2021, 6, 1)

def test_commit_metadata_by_month(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert len(result.project_results) == 1

    project_result = result.project_results[0]
    assert project_result.name == 'testrepo'
    assert len(project_result.commit_results) >= 10

    commit_result = project_result.commit_results[0]
    assert commit_result.hash == '57a6ac0058bef51f396a4322c38db69d5c26c4ff'
    assert commit_result.date == date(2020, 1, 1)

    commit_result = project_result.commit_results[1]
    assert commit_result.hash == '1791c734a04c2984679f980183cf8e4615ea124e'
    assert commit_result.date == date(2020, 2, 1)

def test_metric_names(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric()
    def m2(commit: ParsedCommit):
        return 1
    
    @evo.metric(group='foo')
    def m3(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert result.metric_names == ['m1', 'm2', 'm3']

def test_dates_by_year(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='year')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert result.metric_dates == ['2020', '2021', '2022', '2023', '2024', '2025']

def test_dates_filter(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='year', from_year=2021, to_year=2022)

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert result.metric_dates == ['2021', '2022']

def test_dates_last_version(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='year', last_version_only=True)

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert result.metric_dates == ['2025']

def test_dates_by_month(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run(html=False)

    assert len(result.metric_dates) > 50
    assert result.metric_dates[0] == '01/2020'
    assert result.metric_dates[-1] == '07/2025'

def test_numerical_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2')
    def m2(commit: ParsedCommit):
        return 1.1
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 2
    assert evolutions[0].name == 'm1'
    assert evolutions[0].values == [1, 1, 1, 1, 1, 1]

    assert evolutions[1].name == 'm2'
    assert evolutions[1].values == [1.1, 1.1, 1.1, 1.1, 1.1, 1.1]

def test_invalid_numerical_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 'foo'
    
    with pytest.raises(BadReturnType):
        evo.run(html=False)

def test_numerical_metric_list_aggregate(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')
    
    @evo.metric('m1', aggregate='sum')
    def m1(commit: ParsedCommit):
        return [1,1,1]
    
    @evo.metric('m2', aggregate='mean')
    def m2(commit: ParsedCommit):
        return [1,1,1]
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 2
    assert evolutions[0].values == [3, 3, 3, 3, 3, 3]
    assert evolutions[1].values == [1, 1, 1, 1, 1, 1]

def test_numerical_metric_invalid_list_aggregate(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')
    
    @evo.metric('m1', aggregate='invalid')
    def m1(commit: ParsedCommit):
        return [1,1,1]
    
    with pytest.raises(BadAggregate):
        evo.run(html=False)

def test_categorical_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', categorical=True)
    def m1(commit: ParsedCommit):
        return ['a', 'a', 'a', 'b', 'b', 'c']
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 3
    assert evolutions[0].values == [3, 3, 3, 3, 3, 3]
    assert evolutions[1].values == [2, 2, 2, 2, 2, 2]
    assert evolutions[2].values == [1, 1, 1, 1, 1, 1]

def test_empty_categorical_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', categorical=True)
    def m1(commit: ParsedCommit):
        return []
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()
    
    assert len(evolutions) == 0

def test_invalid_categorical_metric(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', categorical=True)
    def m1(commit: ParsedCommit):
        return 100
    
    with pytest.raises(BadReturnType):
        evo.run(html=False)

def test_ungrouped_metrics(local_repo):
    
    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2')
    def m2(commit: ParsedCommit):
        return 2
    
    result = evo.run(html=False)
    assert len(result.metric_groups) == 2

def test_grouped_metrics(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', group='my metric')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2', group='my metric')
    def m2(commit: ParsedCommit):
        return 2
    
    result = evo.run(html=False)
    assert len(result.metric_groups) == 1

def test_parsed_files_single_extension(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', extension='.py')
    def m1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 1, 1, 1, 1, 1]

def test_parsed_files_multiple_extension(local_repo):

    evo = GitEvo(repo=local_repo)

    @evo.metric('python files', extension='.py')
    def files1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('js files', extension='.js')
    def files2(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('ts files', extension='.ts')
    def files3(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 1, 1, 1, 1, 1]
    assert evolutions[1].values == [0, 1, 1, 1, 1, 1]
    assert evolutions[2].values == [0, 0, 1, 1, 1, 1]

def test_no_parsed_files(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', extension='.xyz')
    def m1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 0, 0, 0, 0, 0]

def test_missing_extension(local_repo):

    evo = GitEvo(repo=local_repo)

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    with pytest.raises(FileExtensionNotFound):
        evo.run(html=False)

def test_loc(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    evo.date_unit = 'month'

    @evo.metric('m1', extension='.py')
    def m1(commit: ParsedCommit):
        return commit.loc
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:7] == [0, 2, 5, 8, 13, 15, 15]

def test_zero_loc(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1', extension='.xyz')
    def m1(commit: ParsedCommit):
        return commit.loc
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 0, 0, 0, 0, 0]

def test_loc_by_type(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'mean')
    
    @evo.metric('m2')
    def m2(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'median')
    
    @evo.metric('m3', aggregate='sum')
    def m3(commit: ParsedCommit):
        return commit.loc_by_type('function_definition')
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:6] == [0, 2, 2, 2, 2.5, 2.5]
    assert evolutions[1].values[0:6] == [0, 2, 2, 2, 2, 2]
    assert evolutions[2].values[0:6] == [0, 2, 4, 6, 10, 10]

def test_invalid_loc_by_type(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py')

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'invalid')
    
    with pytest.raises(BadLOCAggregate):
        evo.run(html=False)

def test_count_nodes_all(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')

    @evo.metric('all_nodes')
    def all_nodes(commit: ParsedCommit):
        return commit.count_nodes()
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()
    assert evolutions[0].values[0:6] == [0, 18, 35, 52, 84, 97]
    
def test_count_nodes_multiple(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')
    
    @evo.metric('functions')
    def functions(commit: ParsedCommit):
        return commit.count_nodes('function_definition')
    
    @evo.metric('classes')
    def classes(commit: ParsedCommit):
        return commit.count_nodes('class_definition')
    
    @evo.metric('functions and classes')
    def functions_and_classes(commit: ParsedCommit):
        return commit.count_nodes(['function_definition', 'class_definition'])
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:6] == [0, 1, 2, 3, 4, 4]
    assert evolutions[1].values[0:6] == [0, 0, 0, 0, 0, 1]
    assert evolutions[2].values[0:6] == [0, 1, 2, 3, 4, 5]

def test_find_node_types_multiple(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')

    @evo.metric('functions and and classes', categorical=True)
    def functions_and_classes(commit: ParsedCommit):
        return commit.find_node_types(['function_definition', 'class_definition'])
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 2

def test_find_node_types_all(local_repo):

    evo = GitEvo(repo=local_repo, extension='.py', date_unit='month')
    
    @evo.metric('all types', categorical=True)
    def all_types(commit: ParsedCommit):
        return commit.find_node_types()
    
    result = evo.run(html=False)
    evolutions = result.metric_evolutions()

    assert len(evolutions) > 20