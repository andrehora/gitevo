import os
from gitevo.cli import GitEvoCLI, main

def test_repo(local_repo, clear_index):
    args = f'{local_repo}'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_report_python(local_repo, clear_index):
    args = f'{local_repo} -r python'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_report_js(local_repo, clear_index):
    args = f'{local_repo} -r js'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_report_ts(local_repo, clear_index):
    args = f'{local_repo} -r ts'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_report_java(local_repo, clear_index):
    args = f'{local_repo} -r java'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_report_fastapi(local_repo, clear_index):
    args = f'{local_repo} -r fastapi'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert not index_contains('bar')

def test_from_to(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -f 2022 -t 2024'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert not index_contains('bar')
    assert not index_contains('2021')
    assert index_contains('2022')
    assert index_contains('2023')
    # assert index_contains('2024')
    # assert not index_contains('2025')

def test_month(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -m'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')

def test_last_version_only(local_repo, clear_index):
    args = f'{local_repo} -r python -l'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert not index_contains('line')
    assert index_contains('bar')

def test_invalid_repo():
    args = 'invalid_repo'.split()
    result = main(args)
    assert result == 1
    assert not index_exists()

def open_index():
    with open('index.html', 'r') as file:
        content = file.read()
    return content

def index_exists():
    return os.path.exists('index.html')

def index_contains(token: str):
    content = open_index()
    return token in content