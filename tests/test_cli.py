import os
from gitevo.cli import GitEvoCLI, main

def test_repo(local_repo, clear_index):
    args = f'{local_repo}'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')
    assert index_contains('2020')
    assert index_contains('2025')

def test_report_python(local_repo, clear_index):
    args = f'{local_repo} -r python'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')
    assert index_contains('2020')
    assert index_contains('2025')

def test_report_js(local_repo, clear_index):
    args = f'{local_repo} -r js'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')
    assert index_contains('2020')
    assert index_contains('2025')

def test_report_ts(local_repo, clear_index):
    args = f'{local_repo} -r ts'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')
    assert index_contains('2020')
    assert index_contains('2025')

def test_report_java(local_repo, clear_index):
    args = f'{local_repo} -r java'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('line')
    assert index_contains('bar')
    assert index_contains('2020')
    assert index_contains('2025')

def test_last_version_only(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -l'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert not index_contains('line')
    assert index_contains('bar')

def test_from(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -f 2022'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()

    assert not index_contains('2021')
    assert index_contains('2022')
    assert index_contains('2023')

def test_to(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -t 2022'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()

    assert index_contains('2020')
    assert index_contains('2021')
    assert index_contains('2022')
    assert not index_contains('2023')

def test_from_to(local_repo, clear_index):
    args = f'{local_repo} -r fastapi -f 2021 -t 2023'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()

    assert not index_contains('2020')
    assert index_contains('2021')
    assert index_contains('2022')
    assert index_contains('2023')
    assert not index_contains('2024')

def test_month(local_repo, clear_index):
    args = f'{local_repo} -m'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert index_exists()
    assert index_contains('01/2020')
    assert index_contains('01/2021')
    assert index_contains('01/2022')
    assert index_contains('01/2023')
    assert index_contains('01/2024')
    assert index_contains('01/2025')

def test_invalid_repo():
    args = 'invalid_repo'.split()
    result = main(args)
    assert result == 1
    assert not index_exists()

def index_exists():
    return os.path.exists('index.html')

def index_contains(token: str):
    content = _open_index()
    return token in content

def _open_index():
    with open('index.html', 'r') as file:
        content = file.read()
    return content