from gitevo import GitEvo, ParsedCommit

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

evo = GitEvo(title='Java', html_filename='index_java.html', 
             repo='./projects_java', extension='.java',
             date_unit='year', from_year=2020)


@evo.metric('Analyzed Java files', aggregate='sum')
def files(commit: ParsedCommit):
    return len(commit.parsed_files)


@evo.metric('Classes, interfaces, and records', aggregate='sum', categorical=True)
def type_definitions(commit: ParsedCommit):
    return commit.node_types(['class_declaration', 'interface_declaration', 'record_declaration'])


@evo.metric('Sealed classes', aggregate='sum')
def type_definitions(commit: ParsedCommit):
    return commit.count_nodes(['sealed'])


@evo.metric('Methods', aggregate='sum')
def type_definitions(commit: ParsedCommit):
    return commit.count_nodes(['method_declaration'])


@evo.metric('Median method LOC', aggregate='median')
def functions(commit: ParsedCommit):
    return commit.loc_for('method_declaration', 'median')


@evo.metric('Conditionals', aggregate='sum', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.node_types(['if_statement', 'switch_expression', 'ternary_expression'])


@evo.metric('Switches', aggregate='sum', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.node_types(['switch_block_statement_group', 'switch_rule'])


@evo.metric('Loops', aggregate='sum', categorical=True, version_chart='donut')
def loops(commit: ParsedCommit):
    return commit.node_types(['for_statement', 'while_statement', 'enhanced_for_statement', 'do_statement'])


@evo.metric('continue vs. break', aggregate='sum', categorical=True)
def continue_break(commit: ParsedCommit):
    return commit.node_types(['break_statement', 'continue_statement'])


@evo.metric('Exception statements', aggregate='sum', categorical=True)
def expections(commit: ParsedCommit):
    return commit.node_types(['try_statement', 'throw_statement'])


@evo.metric('Asserts', aggregate='sum')
def comments(commit: ParsedCommit):
    return commit.count_nodes(['assert_statement'])


@evo.metric('int vs. float', aggregate='sum', categorical=True, version_chart='donut')
def int_float(commit: ParsedCommit):
    return commit.node_types(['integral_type', 'floating_point_type'])


@evo.metric('Strings', aggregate='sum', categorical=True)
def int_float(commit: ParsedCommit):
    return commit.node_types(['string_fragment', 'multiline_string_fragment'])


@evo.metric('Comments', aggregate='sum', categorical=True)
def comments(commit: ParsedCommit):
    return commit.node_types(['block_comment', 'line_comment'])

evo.run()