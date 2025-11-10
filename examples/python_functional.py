from gitevo import GitEvo, ParsedCommit


remote = 'https://github.com/pallets/flask'

evo = GitEvo(repo=remote, extension='.py')

@evo.metric('loc', show_version_chart=False)
def loc(commit: ParsedCommit):
    return commit.loc

@evo.metric('lambda', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('lambda')

@evo.metric('list_comprehension', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('list_comprehension')

@evo.metric('dictionary_comprehension', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('dictionary_comprehension')

@evo.metric('set_comprehension', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('set_comprehension')

@evo.metric('generator_expression', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('generator_expression')

@evo.metric('yield', show_version_chart=True)
def count_dynamic_features(commit: ParsedCommit):
    return commit.count_nodes('yield')

evo.run()