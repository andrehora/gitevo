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
$ gitevo <git_repo> -r <python|js|ts|fastapi>
```

`git_repo` can be a Git remote repositority or a path to a local Git repository.

For example:

```
$ gitevo https://github.com/pallets/flask -r python
$ gitevo https://github.com/expressjs/express -r js
$ gitevo https://github.com/vuejs/core -r ts
$ gitevo https://github.com/mockito/mockito -r java
$ gitevo https://github.com/fastapi/fastapi -r fastapi
```

## Command line arguments

```
$ gitevo --help
usage: gitevo [-h] [-r {python,js,ts,java,fastapi}] [-f FROM_YEAR] [-t TO_YEAR] [-m] [-l] repo

Command line for GitEvo

positional arguments:
  repo                  Git repository to be analyzed. It can be a remote Git repository or a path to a local Git repository.

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
