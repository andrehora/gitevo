
import os
import shutil
import pytest

from git import Repo

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