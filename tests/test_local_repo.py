import pytest
import shutil

from gitevo import GitEvo, ParsedCommit
from git import Repo

@pytest.fixture(scope='module')
def local_repo():
    local_repo_path = 'spotflow'
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=local_repo_path)
    yield local_repo_path
    shutil.rmtree(local_repo_path)

@pytest.fixture
def evo(local_repo):
    return GitEvo(repo=local_repo, extension='.py', date_unit='year')

# @pytest.fixture
# def gitevo_remote_repo():
#     remote_repo = 'https://github.com/andrehora/testrepo'
#     return GitEvo(repo=remote_repo, extension='.py', date_unit='year')

def test_no_metric(evo):
    result = evo.run()
    assert len(result.registered_metrics) == 0

def test_register_single_metric(evo):

    @evo.metric('Single metric')
    def single_metric(commit: ParsedCommit):
        return 1
    result = evo.run()

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

def test_metric_data(evo):

    @evo.metric('foo')
    def foo(commit: ParsedCommit):
        return 123
    
    result = evo.run()

    assert len(result.project_results) == 1

    project_result = result.project_results[0]
    assert project_result.name == 'spotflow'
    assert len(project_result.commit_results) > 0

    commit_result = project_result.commit_results[0]
    assert commit_result.hash is not None
    assert commit_result.date is not None

    metric_value = commit_result.metric_results[0]
    assert metric_value.name == 'foo'
    assert metric_value.value == 123