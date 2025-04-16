[![tests](https://github.com/andrehora/gitevo/actions/workflows/tests.yml/badge.svg)](https://github.com/andrehora/gitevo/actions/workflows/tests.yml)

# GitEvo

Code evolution analysis for Git repositories.
It currently supports Python, JavaScript, TypeScript, and Java.

## Install

```
pip install gitevo
```

## Usage

Analyzing the evolution of a Git repository:

```
$ python -m gitevo <repo_url> -r <python|js|ts|fastapi>
```

For example:

```
$ python -m gitevo https://github.com/pallets/flask -r python
$ python -m gitevo https://github.com/expressjs/express -r js
$ python -m gitevo https://github.com/vuejs/core -r ts
$ python -m gitevo https://github.com/mockito/mockito -r java
$ python -m gitevo https://github.com/fastapi/fastapi -r fastapi
```

## Command line arguments

```
usage: python -m gitevo [-h] [-r {python,js,ts,java,fastapi}] [-f FROM_YEAR] [-t TO_YEAR] [-m] [-l] repo

Command line for GitEvo

positional arguments:
  repo                  Git repository to be analyzed. It can be a remote Git repository or a path a local Git repository.

options:
  -h, --help            show this help message and exit
  -r {python,js,ts,java,fastapi}, --report-type {python,js,ts,java,fastapi}
                        Report type to be generated. Default is python.
  -f FROM_YEAR, --from-year FROM_YEAR
                        Filter commits to be analyzed (from year).
  -t TO_YEAR, --to-year TO_YEAR
                        Filter commits to be analyzed (to year).
  -m, --month           Set to analyze commits by month.
  -l, --last-version-only
                        Set to analyze the last version only.
```

## Command line arguments

```
usage: gitevo [-h] [-r {python,js,ts,java,fastapi}] [-f FROM_YEAR] [-t TO_YEAR] [-m] [-l] repo

Command line for GitEvo

positional arguments:
  repo                  Git repository to be analyzed. It can be a remote Git repository or a path a local Git repository.

options:
  -h, --help            show this help message and exit
  -r {python,js,ts,java,fastapi}, --report-type {python,js,ts,java,fastapi}
                        Report type to be generated. Default is python.
  -f FROM_YEAR, --from-year FROM_YEAR
                        Filter commits to be analyzed (from year).
  -t TO_YEAR, --to-year TO_YEAR
                        Filter commits to be analyzed (to year).
  -m, --month           Set to analyze commits by month.
  -l, --last-version-only
                        Set to analyze the last version only.
```