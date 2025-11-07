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