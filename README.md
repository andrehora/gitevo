[![tests](https://github.com/andrehora/gitevo/actions/workflows/tests.yml/badge.svg)](https://github.com/andrehora/gitevo/actions/workflows/tests.yml)

# GitEvo

Code evolution analysis for Git repositories.
It currently supports Python, JavaScript, TypeScript, and Java.

## Install

```
pip install gitevo
```

## Quick examples

Analyzing the evolution of a Git repository:

```
$ gitevo <repo_url> -r <python|js|ts|fastapi>
```

For example:

```
$ gitevo https://github.com/pallets/flask -r python
$ gitevo https://github.com/expressjs/express -r js
$ gitevo https://github.com/vuejs/core -r ts
$ gitevo https://github.com/mockito/mockito -r java
$ gitevo https://github.com/fastapi/fastapi -r fastapi
```
