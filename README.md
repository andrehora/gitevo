[![tests](https://github.com/andrehora/gitevo/actions/workflows/tests.yml/badge.svg)](https://github.com/andrehora/gitevo/actions/workflows/tests.yml)

# GitEvo

Code evolution analysis for Git repositories.
It currently supports Python, JavaScript, TypeScript, and Java.
GitEvo can also be used to define custom code evolution metrics at the level of the concrete syntax tree (CST), thanks to [Tree-sitter](https://tree-sitter.github.io/tree-sitter).

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

See more examples: [gitevo-examples](https://github.com/andrehora/gitevo-examples).

## Install

```
pip install gitevo
```

## Usage via command-line

Analyzing the evolution of a Git repository:

```shell
$ gitevo -r {python|python_fastapi|javascript|typescript|java} <git_repo>

# For example:
$ gitevo -r python https://github.com/pallets/flask
$ gitevo -r javascript https://github.com/expressjs/express
$ gitevo -r typescript https://github.com/vuejs/core
$ gitevo -r java https://github.com/mockito/mockito
$ gitevo -r python_fastapi https://github.com/fastapi/fastapi
```

`git_repo` accepts (1) a Git URL, (2) a local repository, or (3) a directory containing multiple Git repositories:

```shell
# 1. Git URL
$ gitevo -r python https://github.com/pallets/flask

# 2. Local repository
$ git clone https://github.com/pallets/flask
$ gitevo -r python flask

# 3. Directory containing multiple Git repositories
$ mkdir projects
$ cd projects
$ git clone https://github.com/pallets/flask
$ git clone https://github.com/pallets/click
$ gitevo -r python .
```

### Command-line arguments

```
$ gitevo --help
usage: gitevo [-h] [-r {python,python_fastapi,javascript,typescript,java}] [-f FROM_YEAR] [-t TO_YEAR] [-m] [-v] repo

Command line for GitEvo

positional arguments:
  repo                  Git repository to analyze. Accepts a Git URL, a local Git repository, or a directory containing multiple Git
                        repositories. Example: gitevo https://github.com/pallets/flask

options:
  -h, --help            show this help message and exit
  -r {python,python_fastapi,javascript,typescript,java}, --report {python,python_fastapi,javascript,typescript,java}
                        Report to be generated. Default is python.
  -f FROM_YEAR, --from-year FROM_YEAR
                        Filter commits to be analyzed (from year). Default is today - 5 years.
  -t TO_YEAR, --to-year TO_YEAR
                        Filter commits to be analyzed (to year).
  -m, --month           Set to analyze commits by month.
  -v, --version         Show the GitEvo version.
```

## Defining custom metrics

GitEvo can be used to define custom code evolution metrics at the level of the concrete syntax tree (CST), thanks to [Tree-sitter](https://tree-sitter.github.io/tree-sitter).
GitEvo provides three key classes: `GitEvo`, `ParsedCommit`, and `ParsedFile`.

- `GitEvo` is the main class, the entry point to use the tool.
It receives as input the repository, file extension, date unit for analysis, and start/end year for analysis.

- Metrics are defined in functions decorated with `@evo.metric()`.

- `ParsedCommit` represents a parsed commit and contains (1) a list of `ParsedFile` and (2) a list of [`tree_sitter.Node`](https://tree-sitter.github.io/py-tree-sitter/classes/tree_sitter.Node.html).

- `ParsedFile` represents a parsed file in a commit, including properties as name, path, and tree-sitter nodes.

### Examples

#### Basic metrics

```python
from gitevo import GitEvo, ParsedCommit

remote = 'https://github.com/pallets/flask'
evo = GitEvo(repo=remote, extension='.py')

@evo.metric('Lines of code (LOC)')
def loc(commit: ParsedCommit):
    return commit.loc

@evo.metric('Python files')
def python_files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('Test files')
def test_files(commit: ParsedCommit):
    test_files = [f for f in commit.parsed_files if 'test_' in f.name.lower()]
    return len(test_files)

@evo.metric('LOC / Python files')
def loc_per_file(commit: ParsedCommit):
    python_files = len(commit.parsed_files)
    if python_files == 0: return 0
    return commit.loc / python_files

evo.run()
```

#### Metrics based on node types

```python
from gitevo import GitEvo, ParsedCommit

remote = 'https://github.com/pallets/flask'
evo = GitEvo(repo=remote, extension='.py')

@evo.metric('Data structures', categorical=True)
def data_structures(commit: ParsedCommit):
    data_structure_types = ['dictionary', 'list', 'set', 'tuple']
    return commit.find_node_types(data_structure_types)

@evo.metric('Loops', categorical=True)
def loops(commit: ParsedCommit):
    loop_types = ['for_statement', 'while_statement', 'for_in_clause']
    return commit.find_node_types(loop_types)

evo.run()
```

#### Metrics based on node content

```python
from gitevo import GitEvo, ParsedCommit

remote = 'https://github.com/pallets/flask'
evo = GitEvo(repo=remote, extension='.py')

@evo.metric('Async functions')
def async_functions(commit: ParsedCommit):
    functions = commit.find_nodes_by_type(['function_definition'])
    async_functions = [f for f in functions if as_str(f.child(0).text) == 'async']
    return len(async_functions)

@evo.metric('@pytest decorated functions')
def decorated_functions(commit: ParsedCommit):
    decorators = commit.find_nodes_by_type(['decorated_definition'])
    decorated_functions = [d for d in decorators if d.child_by_field_name('definition').type == 'function_definition']
    pytest_decorated = [dc for dc in decorated_functions if as_str(dc.child(0).text).startswith('@pytest')]
    return len(pytest_decorated)

evo.run()
```

#### More examples

- All: https://github.com/andrehora/gitevo/tree/main/examples
- Python: https://github.com/andrehora/gitevo/blob/main/examples/python.py
- JS: https://github.com/andrehora/gitevo/blob/main/examples/javascript.py
- TS: https://github.com/andrehora/gitevo/blob/main/examples/typescript.py
- Java: https://github.com/andrehora/gitevo/blob/main/examples/java.py
- FastAPI: https://github.com/andrehora/gitevo/blob/main/examples/fastapi.py

#### More info about `tree_sitter.Node`

- `tree_sitter.Node` documentation: https://tree-sitter.github.io/py-tree-sitter/classes/tree_sitter.Node.html
- Python node types: https://github.com/tree-sitter/tree-sitter-python/blob/master/src/node-types.json
- JS node types: https://github.com/tree-sitter/tree-sitter-javascript/blob/master/src/node-types.json
- TS node types: https://github.com/tree-sitter/tree-sitter-typescript/blob/master/typescript/src/node-types.json
- Java node types: https://github.com/tree-sitter/tree-sitter-java/blob/master/src/node-types.json
