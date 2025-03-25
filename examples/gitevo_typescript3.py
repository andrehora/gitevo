from gitevo import GitEvo, ParsedCommit

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

def ratio(a: int, b: int) -> int:
    if b == 0:
        return 0
    return round(a/b, 2)

evo = GitEvo(title='TypeScript', html_filename='index_ts.html', 
             repo='./projects_typescript/playwright', extension='.ts',
             date_unit='year', from_year=2015)



@evo.metric('TypeScript files', aggregate='sum', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('LOC', aggregate='sum', show_version_chart=False)
def files(commit: ParsedCommit):
    return commit.loc



@evo.metric('var total', aggregate='sum', group='let vs. var (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['var'])

@evo.metric('let total', aggregate='sum', group='let vs. var (total)')
def namedtuple(commit: ParsedCommit):
    return commit.count_nodes(['let'])



@evo.metric('var', aggregate='median', group='let vs. var')
def variable_declarations(commit: ParsedCommit):
    var_count = commit.count_nodes(['var'])
    total = commit.loc / 1000
    return ratio(var_count, total)

@evo.metric('let', aggregate='median', group='let vs. var')
def variable_declarations(commit: ParsedCommit):
    let_count = commit.count_nodes(['let'])
    total = commit.loc / 1000
    return ratio(let_count, total)



@evo.metric('arrow function total', aggregate='sum', group='functions (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['arrow_function'])

@evo.metric('function declaration total', aggregate='sum', group='functions (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['function_declaration'])

@evo.metric('function expression total', aggregate='sum', group='functions (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['function_expression'])



@evo.metric('arrow function', aggregate='median', group='functions')
def definitions(commit: ParsedCommit):
    arrow_function_count = commit.count_nodes(['arrow_function'])
    total = commit.loc / 1000
    return ratio(arrow_function_count, total)

@evo.metric('function declaration', aggregate='median', group='functions')
def definitions(commit: ParsedCommit):
    function_declaration_count = commit.count_nodes(['function_declaration'])
    total = commit.loc / 1000
    return ratio(function_declaration_count, total)

@evo.metric('function expression', aggregate='median', group='functions')
def definitions(commit: ParsedCommit):
    function_expression_count = commit.count_nodes(['function_expression'])
    total = commit.loc / 1000
    return ratio(function_expression_count, total)



@evo.metric('interface total', aggregate='sum', group='interface vs. type (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['interface_declaration'])

@evo.metric('type total', aggregate='sum', group='interface vs. type (total)')
def namedtuple(commit: ParsedCommit):
    return commit.count_nodes(['type_alias_declaration'])



@evo.metric('interface', aggregate='median', group='interface vs. type')
def type_definitions(commit: ParsedCommit):
    interface_count = commit.count_nodes(['interface_declaration'])
    total = commit.loc / 1000
    return ratio(interface_count, total)

@evo.metric('type', aggregate='median', group='interface vs. type')
def type_definitions(commit: ParsedCommit):
    type_count = commit.count_nodes(['type_alias_declaration'])
    total = commit.loc / 1000
    return ratio(type_count, total)



@evo.metric('any total', aggregate='sum', group='any vs. unknown (total)')
def dataclass(commit: ParsedCommit):
    return commit.count_nodes(['any'])

@evo.metric('unknown total', aggregate='sum', group='any vs. unknown (total)')
def namedtuple(commit: ParsedCommit):
    return commit.count_nodes(['unknown'])



@evo.metric('any', aggregate='median', group='any vs. unknown')
def type_definitions(commit: ParsedCommit):
    any_count = commit.count_nodes(['any'])
    total = commit.loc / 1000
    return ratio(any_count, total)

@evo.metric('unknown', aggregate='median', group='any vs. unknown')
def type_definitions(commit: ParsedCommit):
    unknown_count = commit.count_nodes(['unknown'])
    total = commit.loc / 1000
    return ratio(unknown_count, total)


evo.run()