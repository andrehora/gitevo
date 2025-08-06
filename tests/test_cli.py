import os
from gitevo.cli import GitEvoCLI, main, gitevo_version

def test_repo(local_repo, clear_reports):
    args = f'{local_repo}'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('line')
    assert report_contains('bar')
    assert report_contains('2020')
    assert report_contains('2025')

def test_report_python(local_repo, clear_reports):
    args = f'{local_repo} -r python'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('line')
    assert report_contains('bar')
    assert report_contains('2020')
    assert report_contains('2025')

def test_report_js(local_repo, clear_reports):
    args = f'{local_repo} -r javascript'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('line')
    assert report_contains('bar')
    assert report_contains('2020')
    assert report_contains('2025')

def test_report_ts(local_repo, clear_reports):
    args = f'{local_repo} -r typescript'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('line')
    assert report_contains('bar')
    assert report_contains('2020')
    assert report_contains('2025')

def test_report_java(local_repo, clear_reports):
    args = f'{local_repo} -r java'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('line')
    assert report_contains('bar')
    assert report_contains('2020')
    assert report_contains('2025')

def test_from(local_repo, clear_reports):
    args = f'{local_repo} -r python_fastapi -f 2022'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()

    assert not report_contains('2021')
    assert report_contains('2022')
    assert report_contains('2023')

def test_to(local_repo, clear_reports):
    args = f'{local_repo} -r python_fastapi -t 2022'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()

    assert report_contains('2020')
    assert report_contains('2021')
    assert report_contains('2022')
    assert not report_contains('2023')

def test_from_to(local_repo, clear_reports):
    args = f'{local_repo} -r python_fastapi -f 2021 -t 2023'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()

    assert not report_contains('2020')
    assert report_contains('2021')
    assert report_contains('2022')
    assert report_contains('2023')
    assert not report_contains('2024')

def test_month(local_repo, clear_reports):
    args = f'{local_repo} -m'.split()
    result = GitEvoCLI(args).run()
    assert result == 0
    assert report_exists()
    assert report_contains('01/2020')
    assert report_contains('01/2021')
    assert report_contains('01/2022')
    assert report_contains('01/2023')
    assert report_contains('01/2024')
    assert report_contains('01/2025')

def test_invalid_repo():
    args = 'invalid_repo'.split()
    result = main(args)
    assert result == 1
    assert not report_exists()

def test_version():
    assert 'GitEvo ' in gitevo_version()

def report_exists():
    return os.path.exists('report_testrepo.html')

def report_contains(token: str):
    content = _open_report()
    return token in content

def _open_report():
    with open('report_testrepo.html', 'r') as file:
        content = file.read()
    return content