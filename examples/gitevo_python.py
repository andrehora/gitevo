from gitevo import GitEvo, ParsedCommit
import tree_sitter_python


def as_str(text: bytes) -> str:
    return text.decode('utf-8')

evo = GitEvo(title='Python', html_filename='index_python.html', 
             repo='./projects_python/cli', extension='.py', 
             date_unit='year', from_year=2020, last_version_only=False)
# evo.add_language('.py', tree_sitter_python.language())


@evo.metric('Analyzed Python files', aggregate='sum', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)


@evo.metric('Most used data structures', aggregate='sum', categorical=True)
def data_structures(commit: ParsedCommit):
    return commit.node_types(['dictionary', 'list', 'set', 'tuple'])


@evo.metric('Most used comprehensions', aggregate='sum', categorical=True)
def comprehensions(commit: ParsedCommit):
    return commit.node_types(['dictionary_comprehension', 'list_comprehension', 'set_comprehension'])


@evo.metric('Definitions', aggregate='sum', categorical=True)
def definitions(commit: ParsedCommit):
    return commit.node_types(['class_definition', 'function_definition', 'decorated_definition'])


@evo.metric('class_loc', aggregate='median', group='Median definition LOC')
def class_loc(commit: ParsedCommit):
    return commit.loc_for('class_definition', 'median')


@evo.metric('function_loc', aggregate='median', group='Median definition LOC')
def function_loc(commit: ParsedCommit):
    return commit.loc_for('function_definition', 'median')


@evo.metric('decorated_loc', aggregate='median', group='Median definition LOC')
def decorated_loc(commit: ParsedCommit):
    return commit.loc_for('decorated_definition', 'median')


@evo.metric('Decorators: @dataclass', aggregate='sum')
def definitions(commit: ParsedCommit):
    decorated_definitions = commit.find_nodes_by_type(['decorated_definition'])
    decorated_classes = [decorated_definition for decorated_definition in decorated_definitions if decorated_definition.child_by_field_name('definition').type == 'class_definition']
    dataclasses = [decorated_class for decorated_class in decorated_classes if as_str(decorated_class.child(0).text).startswith('@dataclass')]
    return len(dataclasses)


@evo.metric('Decorators: @classmethod and @staticmethod', aggregate='sum', categorical=True)
def definitions(commit: ParsedCommit):
    decorated_definitions = commit.find_nodes_by_type(['decorated_definition'])
    decorated_functions = [decorated_definition for decorated_definition in decorated_definitions if decorated_definition.child_by_field_name('definition').type == 'function_definition']
    classmethods = ['@classmethod' for decorated_function in decorated_functions if as_str(decorated_function.child(0).text).startswith('@classmethod')]
    staticmethods = ['@staticmethod' for decorated_function in decorated_functions if as_str(decorated_function.child(0).text).startswith('@staticmethod')]
    return classmethods + staticmethods


@evo.metric('Functions: def vs. async def', categorical=True, aggregate='sum', version_chart_type='donut')
def sync_async(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    return ['async def' if as_str(func.child(0).text) == 'async' else 'def' for func in function_definitions]


@evo.metric('Functions: return types', categorical=True, aggregate='sum', version_chart_type='donut')
def return_types(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    return ['return_type' if func.child_by_field_name('return_type') else 'no return_type' for func in function_definitions]


@evo.metric('Functions: parameter types', categorical=True, aggregate='sum', version_chart_type='hbar', top_n=5)
def parameter_types(commit: ParsedCommit):
    function_definitions = commit.find_nodes_by_type(['function_definition'])
    func_def_parameters = [func.child_by_field_name('parameters') for func in function_definitions if func.child_by_field_name('parameters')]
    return [named_param.type for parameters in func_def_parameters for named_param in commit.named_children(parameters)]


@evo.metric('Import statements', categorical=True, version_chart_type='donut')
def imports(commit: ParsedCommit):
    return commit.node_types(['import_statement', 'import_from_statement', 'future_import_statement'])


@evo.metric('Exception statements', aggregate='sum', categorical=True)
def exceptions(commit: ParsedCommit):
    return commit.node_types(['try_statement', 'raise_statement'])


@evo.metric('Control flow statements', aggregate='sum', categorical=True)
def control_flow(commit: ParsedCommit):
    return commit.node_types(['for_statement', 'while_statement', 'if_statement', 'try_statement', 'match_statement', 'with_statement'])


@evo.metric('Control flow statements', aggregate='sum', categorical=True)
def control_flow(commit: ParsedCommit):
    return commit.node_types(['for_statement', 'while_statement', 'if_statement', 'try_statement', 'match_statement', 'with_statement'])


@evo.metric('Conditionals', aggregate='sum', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.node_types(['if_statement', 'conditional_expression'])


@evo.metric('Loops', aggregate='sum', categorical=True, version_chart_type='donut')
def for_while(commit: ParsedCommit):
    return commit.node_types(['for_statement', 'while_statement', 'for_in_clause'])


@evo.metric('continue vs. break', aggregate='sum', categorical=True)
def continue_break(commit: ParsedCommit):
    return commit.node_types(['break_statement', 'continue_statement'])


@evo.metric('integer vs. float', aggregate='sum', categorical=True, version_chart_type='donut')
def int_float(commit: ParsedCommit):
    return commit.node_types(['integer', 'float'])


@evo.metric('return vs. yield', aggregate='sum', categorical=True, version_chart_type='donut')
def return_yield(commit: ParsedCommit):
    return commit.node_types(['return_statement', 'yield'])


@evo.metric('Keyword: assert', aggregate='sum')
def asserts(commit: ParsedCommit):
    return commit.count_nodes(['assert_statement'])


@evo.metric('Keyword: lambda', aggregate='sum')
def lambdas(commit: ParsedCommit):
    return commit.count_nodes(['lambda'])


@evo.metric('Keyword: await', aggregate='sum')
def awaits(commit: ParsedCommit):
    return commit.count_nodes(['await'])


@evo.metric('Keyword: pass', aggregate='sum')
def passes(commit: ParsedCommit):
    return commit.count_nodes(['pass_statement'])


@evo.metric('ellipsis', aggregate='sum')
def passes(commit: ParsedCommit):
    return commit.count_nodes(['ellipsis'])


@evo.metric('Aliased imports', aggregate='sum')
def imports(commit: ParsedCommit):
    return commit.count_nodes(['aliased_import'])

evo.run()
