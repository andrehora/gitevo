import os
from gitevo.cli import GitEvoCLI, main

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