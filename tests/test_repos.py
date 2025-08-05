
from git import Repo
from gitevo import GitEvo
from tests.conftest import remove_folder_if_exists


def test_remote_git_repository():

    remove_folder_if_exists('testrepo')

    remote_repo = 'https://github.com/andrehora/testrepo'
    evo = GitEvo(repo=remote_repo, extension='.py')
    result = evo.run()

    assert len(result) == 1

    remove_folder_if_exists('testrepo')

def test_local_git_repository():

    folder_name = 'projects'
    remove_folder_if_exists(folder_name)
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path='projects/testrepo')
    Repo.clone_from(url='https://github.com/andrehora/library', to_path='projects/library')

    evo = GitEvo(repo='projects/testrepo', extension='.py')
    result = evo.run()
    assert len(result) == 1

    evo = GitEvo(repo='projects/library', extension='.py')
    result = evo.run()
    assert len(result) == 1

    evo = GitEvo(repo='projects', extension='.py')
    result = evo.run()
    assert len(result) == 2

    remove_folder_if_exists(folder_name)