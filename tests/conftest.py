
import os
import shutil
import pytest

from git import Repo

@pytest.fixture(scope='module')
def local_repo():
    repo_folder = 'testrepo'
    remove_folder_if_exists(repo_folder)
    repo = Repo.clone_from(url='https://github.com/andrehora/testrepo', to_path=repo_folder)
    yield repo_folder
    repo.close()
    remove_folder_if_exists(repo_folder)

@pytest.fixture
def clear_index():
    remove_file_if_exists('index.html')
    yield
    remove_file_if_exists('index.html')

def remove_folder_if_exists(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name, onerror=onerror)

def remove_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)

def onerror(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise