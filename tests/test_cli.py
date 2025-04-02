import pytest
import os
import shutil
from git import Repo
from gitevo.cli import GitEvoCLI, main

def remove_folder_if_exists(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

def remove_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)

@pytest.fixture(scope='module')
def local_repo():
    repo_folder = 'testrepo'
    remove_folder_if_exists(repo_folder)
    Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=repo_folder)
    yield repo_folder
    remove_folder_if_exists(repo_folder)

@pytest.fixture
def clear_index():
    remove_file_if_exists('index.html')
    yield
    remove_file_if_exists('index.html')

def test_repo_python(local_repo, clear_index):
    args = f'{local_repo}'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

    args = f'{local_repo} -r python'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_repo_js(local_repo, clear_index):
    args = f'{local_repo} -r js'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_repo_ts(local_repo, clear_index):
    args = f'{local_repo} -r ts'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_repo_java(local_repo, clear_index):
    args = f'{local_repo} -r java'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_repo_fastapi(local_repo, clear_index):
    args = f'{local_repo} -r fastapi'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_date_range(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -f 2022 -t 2023'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_month(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -m'.split()
    result = GitEvoCLI(args).run()
    assert os.path.exists('index.html')
    assert result == 0

def test_invalid_repo():
    args = 'invalid_repo'.split()
    result = main(args)
    assert result == 1