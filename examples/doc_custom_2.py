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