from gitevo import GitEvo, ParsedCommit

def as_str(text: bytes) -> str:
    return text.decode('utf-8')

evo = GitEvo(title='TypeScript', html_filename='index_ts.html', 
             repo='./projects_typescript', extension='.ts',
             date_unit='year', from_year=2020)


@evo.metric('Analyzed TypeScript files', aggregate='sum')
def files(commit: ParsedCommit):
    return len(commit.parsed_files)


@evo.metric('Classes, interfaces, and type aliases', aggregate='sum', categorical=True)
def type_definitions(commit: ParsedCommit):
    return commit.node_types(['class_declaration', 'interface_declaration', 'type_alias_declaration'])


@evo.metric('Variable declarations', aggregate='sum', categorical=True, version_chart='donut')
def variable_declarations(commit: ParsedCommit):
    return commit.node_types(['const', 'let', 'var'])


@evo.metric('Variables: typed vs. untyped', aggregate='sum', categorical=True, version_chart='donut')
def variables(commit: ParsedCommit):
    return ['typed_var' if var.child_by_field_name('type') else 'untyped_var' for var in commit.find_nodes_by_type(['variable_declarator'])]


@evo.metric('Types: any vs. unknown', aggregate='sum', categorical=True)
def expections(commit: ParsedCommit):
    return commit.node_types(['any', 'unknown'])


@evo.metric('Function/methods', aggregate='sum', categorical=True)
def function_definitions(commit: ParsedCommit):
    nodes = ['function_declaration', 'method_definition', 'generator_function_declaration', 'arrow_function', 'generator_function', 'function_expression']
    return commit.node_types(nodes)


@evo.metric('Function/method signatures', aggregate='sum', categorical=True)
def signatures(commit: ParsedCommit):
    return commit.node_types(['function_signature', 'method_signature', 'abstract_method_signature'])


@evo.metric('Function/method return types', aggregate='sum', categorical=True, version_chart='donut')
def return_type(commit: ParsedCommit):
    ts_nodes = ['abstract_method_signature', 'function_signature', 'method_signature', 'call_signature', 'function_type']
    js_nodes = ['function_declaration', 'method_definition', 'generator_function_declaration', 'arrow_function', 'generator_function', 'function_expression']
    nodes = ts_nodes+js_nodes
    return ['return_type' if var.child_by_field_name('return_type') else 'no return_type' for var in commit.find_nodes_by_type(nodes)]


@evo.metric('Parameters: typed vs. untyped', aggregate='sum', categorical=True, version_chart='donut')
def parameters(commit: ParsedCommit):
    return ['typed_param' if var.child_by_field_name('type') else 'untyped_param' for var in commit.find_nodes_by_type(['required_parameter', 'optional_parameter'])]


@evo.metric('Parameters: required vs. optional', aggregate='sum', categorical=True, version_chart='donut')
def req_opt_parameters(commit: ParsedCommit):
    return commit.node_types(['required_parameter', 'optional_parameter'])


@evo.metric('Conditionals', aggregate='sum', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.node_types(['if_statement', 'switch_statement', 'ternary_expression'])


@evo.metric('Loops', aggregate='sum', categorical=True, version_chart='donut')
def loops(commit: ParsedCommit):
    return commit.node_types(['for_statement', 'while_statement', 'for_in_statement', 'do_statement'])


@evo.metric('continue vs. break', aggregate='sum', categorical=True)
def continue_break(commit: ParsedCommit):
    return commit.node_types(['break_statement', 'continue_statement'])


@evo.metric('Exception statements', aggregate='sum', categorical=True)
def expections(commit: ParsedCommit):
    return commit.node_types(['try_statement', 'throw_statement'])


@evo.metric('Await expression', aggregate='sum')
def await_expression(commit: ParsedCommit):
    return commit.count_nodes(['await_expression'])


@evo.metric('Comments', aggregate='sum')
def comments(commit: ParsedCommit):
    return commit.count_nodes(['comment'])

evo.run()