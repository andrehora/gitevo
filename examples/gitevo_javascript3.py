from gitevo import GitEvo, ParsedCommit

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

def ratio(a: int, b: int) -> int:
    if b == 0:
        return 0
    return round(a/b, 2)

evo = GitEvo(title='JavaScript', html_filename='index_js.html', 
             repo='./projects_javascript/express', extension='.js', 
             date_unit='year', from_year=2015)



@evo.metric('JavaScript files', aggregate='sum', show_version_chart=False)
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

evo.run()
