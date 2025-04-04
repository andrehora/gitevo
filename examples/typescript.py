from gitevo import GitEvo, ParsedCommit


remote = 'https://github.com/vuejs/core'
# remote = 'https://github.com/microsoft/vscode'
# remote = 'https://github.com/angular/angular'
# remote = 'https://github.com/microsoft/playwright'
# remote = 'https://github.com/storybookjs/storybook'

evo = GitEvo(repo=remote, extension='.ts')

@evo.metric('Lines of code (LOC)', show_version_chart=False)
def loc(commit: ParsedCommit):
    return commit.loc

@evo.metric('TypeScript files', aggregate='sum', show_version_chart=False)
def files(commit: ParsedCommit):
    return len(commit.parsed_files)

@evo.metric('LOC / TypeScript files', show_version_chart=False)
def loc_per_file(commit: ParsedCommit):
    parsed_files = len(commit.parsed_files)
    if parsed_files == 0: return 0
    return commit.loc / parsed_files

@evo.metric('Classes, interfaces, and type aliases', aggregate='sum', categorical=True)
def type_definitions(commit: ParsedCommit):
    return commit.find_node_types(['class_declaration', 'interface_declaration', 'type_alias_declaration'])

@evo.metric('Types: any vs. unknown', aggregate='sum', categorical=True)
def any_unknown(commit: ParsedCommit):
    return commit.find_node_types(['any', 'unknown'])

@evo.metric('Variables: typed vs. untyped', aggregate='sum', categorical=True)
def variables(commit: ParsedCommit):
    return ['typed' if var.child_by_field_name('type') else 'untyped' for var in commit.find_nodes_by_type(['variable_declarator'])]

@evo.metric('Variable declarations', aggregate='sum', categorical=True)
def variable_declarations(commit: ParsedCommit):
    return commit.find_node_types(['const', 'let', 'var'])

@evo.metric('Functions', aggregate='sum', categorical=True)
def functions(commit: ParsedCommit):
    method_nodes = ['function_declaration', 'method_definition', 'generator_function_declaration', 
                    'arrow_function', 'generator_function', 'function_expression']
    return commit.find_node_types(method_nodes)

@evo.metric('Conditionals', aggregate='sum', categorical=True)
def conditionals(commit: ParsedCommit):
    return commit.find_node_types(['if_statement', 'switch_statement', 'ternary_expression'])

@evo.metric('Loops', aggregate='sum', categorical=True)
def loops(commit: ParsedCommit):
    return commit.find_node_types(['for_statement', 'while_statement', 'for_in_statement', 'do_statement'])

@evo.metric('Exception statements', aggregate='sum', categorical=True)
def expections(commit: ParsedCommit):
    return commit.find_node_types(['try_statement', 'throw_statement'])

@evo.metric('Await expression', aggregate='sum', categorical=True, show_version_chart=False)
def await_expression(commit: ParsedCommit):
    return commit.find_node_types(['await_expression'])

@evo.metric('Comments', aggregate='sum', categorical=True, show_version_chart=False)
def comments(commit: ParsedCommit):
    return commit.find_node_types(['comment'])

evo.run()