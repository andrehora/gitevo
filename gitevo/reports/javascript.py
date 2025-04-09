from gitevo import GitEvo, ParsedCommit


extension = '.js'

def metrics(evo: GitEvo):

    @evo.metric('Lines of code (LOC)', show_version_chart=False)
    def loc(commit: ParsedCommit):
        return commit.loc

    @evo.metric('JavaScript files', aggregate='sum', show_version_chart=False)
    def files(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('LOC / JavaScript files', show_version_chart=False)
    def loc_per_file(commit: ParsedCommit):
        parsed_files = len(commit.parsed_files)
        if parsed_files == 0: return 0
        return commit.loc / parsed_files

    @evo.metric('Classes', aggregate='sum', categorical=True)
    def classes(commit: ParsedCommit):
        return commit.find_node_types(['class_declaration'])

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