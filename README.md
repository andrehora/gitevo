[![tests](https://github.com/andrehora/gitevo/actions/workflows/tests.yml/badge.svg)](https://github.com/andrehora/gitevo/actions/workflows/tests.yml)

# GitEvo

Code evolution analysis for Git repositories.
It currently supports Python, JavaScript, TypeScript, and Java.
Examples of reports: 
[Flask](https://andrehora.github.io/gitevo-examples/python/flask.html),
[Pandas](https://andrehora.github.io/gitevo-examples/python/pandas.html),
[Node](https://andrehora.github.io/gitevo-examples/javascript/node.html),
[Express](https://andrehora.github.io/gitevo-examples/javascript/express.html),
[TypeScript](https://andrehora.github.io/gitevo-examples/typescript/typescript.html),
[Vue-core](https://andrehora.github.io/gitevo-examples/typescript/vuejs-core.html),
[Spring Boot](https://andrehora.github.io/gitevo-examples/java/spring-boot.html),
[Mockito](https://andrehora.github.io/gitevo-examples/java/mockito.html), and
[FastAPI](https://andrehora.github.io/gitevo-examples/fastapi/fastapi.html).

More examples: [gitevo-examples](https://github.com/andrehora/gitevo-examples).

## Install

```
pip install gitevo
```

## Usage

Analyzing the evolution of a Git repository:

```
$ gitevo -r <python|js|ts|fastapi> <git_repo>
```

For example:

```
$ gitevo -r python https://github.com/pallets/flask
$ gitevo -r js https://github.com/expressjs/express
$ gitevo -r ts https://github.com/vuejs/core
$ gitevo -r java https://github.com/mockito/mockito
$ gitevo -r fastapi https://github.com/fastapi/fastapi
```

`git_repo` accepts (1) a Git URL, (2) a path to a local repository, or (3) a directory containing multiple Git repositories:

```
# 1. Git URL
gitevo -r python https://github.com/pallets/flask

# 2. Path to a local repository
git clone https://github.com/pallets/flask
gitevo -r python flask

# 3. Directory containing multiple Git repositories
mkdir projects
cd projects
git clone https://github.com/pallets/flask
git clone https://github.com/pallets/click
gitevo -r python .
```

## Command line arguments

```
$ gitevo --help
usage: gitevo [-h] [-r {python,js,ts,java,fastapi}] [-f FROM_YEAR] [-t TO_YEAR] [-m] [-l] [-v] repo

Command line for GitEvo

positional arguments:
  repo                  Git repository to analyze. Accepts a Git URL, a path to a local repository, or a directory containing multiple Git
                        repositories

options:
  -h, --help            show this help message and exit
  -r {python,js,ts,java,fastapi}, --report-type {python,js,ts,java,fastapi}
                        Report type to be generated. Default is python.
  -f FROM_YEAR, --from-year FROM_YEAR
                        Filter commits to be analyzed (from year). Default is today - 5 years.
  -t TO_YEAR, --to-year TO_YEAR
                        Filter commits to be analyzed (to year).
  -m, --month           Set to analyze commits by month.
  -l, --last-version-only
                        Set to analyze the last version only.
  -v, --version         Show the GitEvo version.
```
