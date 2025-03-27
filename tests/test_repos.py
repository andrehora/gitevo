
import os
import shutil

from git import Repo
from gitevo import GitEvo


def test_single_remote_repository():

    remote_repo = 'https://github.com/andrehora/testrepo'
    evo = GitEvo(repo=remote_repo, extension='.py')
    result = evo.run()

    assert len(result.project_results) == 1

def test_multiple_remote_repositories():

    remote_repos = ['https://github.com/andrehora/testrepo', 'https://github.com/andrehora/lib']
    evo = GitEvo(repo=remote_repos, extension='.py')
    result = evo.run()

    assert len(result.project_results) == 2

def test_single_local_repository():

    local_repo = 'testrepo'
    remove_folder_if_exists(local_repo)
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=local_repo)

    evo = GitEvo(repo=local_repo, extension='.py')
    result = evo.run()

    assert len(result.project_results) == 1

    remove_folder_if_exists(local_repo)

def test_multiple_local_repositories():

    local_repos = ['testrepo', 'lib']
    remove_folder_if_exists(local_repos[0])
    remove_folder_if_exists(local_repos[1])

    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path='testrepo')
    Repo.clone_from(url='https://github.com/andrehora/lib', to_path='lib')

    evo = GitEvo(repo=local_repos, extension='.py')
    result = evo.run()

    assert len(result.project_results) == 2

    remove_folder_if_exists(local_repos[0])
    remove_folder_if_exists(local_repos[1])

def test_folder_with_multiple_repositories():

    folder_name = 'projects'
    remove_folder_if_exists(folder_name)
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path='projects/testrepo')
    Repo.clone_from(url='https://github.com/andrehora/lib', to_path='projects/lib')

    evo = GitEvo(repo=folder_name, extension='.py')
    result = evo.run()

    assert len(result.project_results) == 2

    remove_folder_if_exists(folder_name)

def remove_folder_if_exists(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)