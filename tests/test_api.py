import pytest
import shutil

from datetime import date
from git import Repo
from gitevo import GitEvo, ParsedCommit
from gitevo.exceptions import BadReturnType, BadAggregate, BadLOCAggregate


@pytest.fixture(scope='module')
def local_repo():
    repo_folder = 'testrepo'
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=repo_folder)
    yield repo_folder
    shutil.rmtree(repo_folder)

@pytest.fixture
def evo(local_repo):
    return GitEvo(repo=local_repo, extension='.py', date_unit='year')


def test_register_single_metric(evo):

    @evo.metric('Single metric')
    def single_metric(commit: ParsedCommit):
        return 1
    
    result = evo.run()
    assert result.registered_metrics[0].name == 'Single metric'

    assert len(result.registered_metrics) == 1
    assert result.registered_metrics[0].name == 'Single metric'
    assert result.registered_metrics[0].group == 'Single metric'
    assert result.registered_metrics[0].file_extension == '.py'
    assert result.registered_metrics[0].callback == single_metric

def test_register_multiple_metrics(evo):

    @evo.metric('Metric 1')
    def m1(commit: ParsedCommit):
        return 1

    @evo.metric('Metric 2')
    def m2(commit: ParsedCommit):
        return 2

    result = evo.run()

    assert len(result.registered_metrics) == 2

    assert result.registered_metrics[0].name == 'Metric 1'
    assert result.registered_metrics[1].name == 'Metric 2'

    assert result.registered_metrics[0].group == 'Metric 1'
    assert result.registered_metrics[1].group == 'Metric 2'

    assert result.registered_metrics[0].file_extension == '.py'
    assert result.registered_metrics[1].file_extension == '.py'

    assert result.registered_metrics[0].callback == m1
    assert result.registered_metrics[1].callback == m2

def test_no_metric(evo):
    result = evo.run()
    assert len(result.registered_metrics) == 0

def test_unamed_metric_has_method_name(evo):

    @evo.metric()
    def my_metric_name(commit: ParsedCommit):
        return 1
    
    result = evo.run()
    assert result.registered_metrics[0].name == 'my_metric_name'
    assert result.registered_metrics[0].group == 'my_metric_name'

def test_commit_metadata_year(evo):

    evo.date_unit = 'year'

    @evo.metric('foo')
    def foo(commit: ParsedCommit):
        return 1
    
    result = evo.run()

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

def test_commit_metadata_month(evo):

    evo.date_unit = 'month'

    @evo.metric('foo')
    def foo(commit: ParsedCommit):
        return 1
    
    result = evo.run()

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

def test_dates_year(evo):

    evo.date_unit = 'year'

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run()

    assert result.metric_dates == ['2020', '2021', '2022', '2023']

def test_dates_month(evo):

    evo.date_unit = 'month'

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    result = evo.run()

    assert len(result.metric_dates) == 43
    assert result.metric_dates[0] == '01/2020'
    assert result.metric_dates[-1] == '07/2023'

def test_numerical_metric(evo):

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2')
    def m2(commit: ParsedCommit):
        return 1.1
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 2
    assert evolutions[0].name == 'm1'
    assert evolutions[0].values == [1, 1, 1, 1]

    assert evolutions[1].name == 'm2'
    assert evolutions[1].values == [1.1, 1.1, 1.1, 1.1]

def test_invalid_numerical_metric(evo):

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 'foo'
    
    with pytest.raises(BadReturnType):
        evo.run()

def test_numerical_metric_list_aggregate(evo):
    
    @evo.metric('m1', aggregate='sum')
    def m1(commit: ParsedCommit):
        return [1,1,1]
    
    @evo.metric('m2', aggregate='mean')
    def m2(commit: ParsedCommit):
        return [1,1,1]
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 2
    assert evolutions[0].values == [3, 3, 3, 3]
    assert evolutions[1].values == [1, 1, 1, 1]

def test_numerical_metric_invalid_list_aggregate(evo):
    
    @evo.metric('m1', aggregate='invalid')
    def m1(commit: ParsedCommit):
        return [1,1,1]
    
    with pytest.raises(BadAggregate):
        evo.run()

def test_categorical_metric(evo):

    @evo.metric('foo', categorical=True)
    def foo(commit: ParsedCommit):
        return ['a', 'a', 'a', 'b', 'b', 'c']
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert len(evolutions) == 3
    assert evolutions[0].values == [3, 3, 3, 3]
    assert evolutions[1].values == [2, 2, 2, 2]
    assert evolutions[2].values == [1, 1, 1, 1]

def test_invalid_categorical_metric(evo):

    @evo.metric('foo', categorical=True)
    def foo(commit: ParsedCommit):
        return 100
    
    with pytest.raises(BadReturnType):
        evo.run()

def test_ungrouped_metrics(evo):

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2')
    def m2(commit: ParsedCommit):
        return 2
    
    result = evo.run()
    assert len(result.metric_groups) == 2

def test_grouped_metrics(evo):

    @evo.metric('m1', group='my metric')
    def m1(commit: ParsedCommit):
        return 1
    
    @evo.metric('m2', group='my metric')
    def m2(commit: ParsedCommit):
        return 2
    
    result = evo.run()
    assert len(result.metric_groups) == 1

def test_parsed_files_single_language(evo):

    @evo.metric('m1', extension='.py')
    def m1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 1, 1, 1]

def test_parsed_files_multiple_languages(evo):

    @evo.metric('python files', extension='.py')
    def files1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('js files', extension='.js')
    def files2(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('ts files', extension='.ts')
    def files3(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 1, 1, 1]
    assert evolutions[1].values == [0, 1, 1, 1]
    assert evolutions[2].values == [0, 0, 1, 1]

def test_zero_parsed_files(evo):

    @evo.metric('m1', extension='.xyz')
    def m1(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 0, 0, 0]

def test_loc(evo):

    evo.date_unit = 'month'

    @evo.metric('m1', extension='.py')
    def m1(commit: ParsedCommit):
        return commit.loc
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:7] == [0, 2, 5, 8, 13, 15, 15]

def test_zero_loc(evo):

    @evo.metric('m1', extension='.xyz')
    def m1(commit: ParsedCommit):
        return commit.loc
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values == [0, 0, 0, 0]

def test_loc_by_type(evo):

    evo.date_unit = 'month'

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'mean')
    
    @evo.metric('m2')
    def m1(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'median')
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:6] == [0, 2, 2, 2, 2.5, 2.5]
    assert evolutions[1].values[0:6] == [0, 2, 2, 2, 2, 2]

def test_invalid_loc_by_type(evo):

    @evo.metric('m1')
    def m1(commit: ParsedCommit):
        return commit.loc_by_type('function_definition', 'invalid')
    
    with pytest.raises(BadLOCAggregate):
        evo.run()

def test_nodes(evo):

    evo.date_unit = 'month'

    @evo.metric('all_nodes')
    def all_nodes(commit: ParsedCommit):
        return commit.count_nodes()
    
    @evo.metric('functions')
    def functions(commit: ParsedCommit):
        return commit.count_nodes('function_definition')
    
    @evo.metric('functions2')
    def functions2(commit: ParsedCommit):
        return commit.count_nodes(['function_definition'])
    
    result = evo.run()
    evolutions = result.metric_evolutions()

    assert evolutions[0].values[0:6] == [0, 18, 35, 52, 84, 97]
    assert evolutions[1].values[0:6] == [0, 1, 2, 3, 4, 4]
    assert evolutions[2].values[0:6] == [0, 1, 2, 3, 4, 4]
    
