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