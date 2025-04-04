from gitevo import GitEvo, ParsedCommit


extension = '.java'
    
def metrics(evo: GitEvo):

    @evo.metric('Lines of code (LOC)', show_version_chart=False)
    def loc(commit: ParsedCommit):
        return commit.loc

    @evo.metric('Java files', aggregate='sum', show_version_chart=False)
    def files(commit: ParsedCommit):
        return len(commit.parsed_files)
    
    @evo.metric('LOC / Java files', show_version_chart=False)
    def loc_per_file(commit: ParsedCommit):
        parsed_files = len(commit.parsed_files)
        if parsed_files == 0: return 0
        return commit.loc / parsed_files
    
    @evo.metric('production file', show_version_chart=False, group='Production and test files')
    def production_files(commit: ParsedCommit):
        return len([file for file in commit.parsed_files if 'test' not in file.name])
    
    @evo.metric('test file', show_version_chart=False, group='Production and test files')
    def test_files(commit: ParsedCommit):
        return len([file for file in commit.parsed_files if 'test' in file.name])

    @evo.metric('Classes, interfaces, and records', aggregate='sum', categorical=True)
    def type_definitions(commit: ParsedCommit):
        return commit.find_node_types(['class_declaration', 'interface_declaration', 'record_declaration'])

    @evo.metric('Methods', aggregate='sum', show_version_chart=False)
    def methods(commit: ParsedCommit):
        return commit.count_nodes(['method_declaration'])

    @evo.metric('LOC of methods (mean)', aggregate='mean', show_version_chart=False)
    def methods_loc(commit: ParsedCommit):
        return commit.loc_by_type('method_declaration', 'mean')

    @evo.metric('Conditionals', aggregate='sum', categorical=True)
    def conditionals(commit: ParsedCommit):
        return commit.find_node_types(['if_statement', 'switch_expression', 'ternary_expression'])

    @evo.metric('Loops', aggregate='sum', categorical=True)
    def loops(commit: ParsedCommit):
        return commit.find_node_types(['for_statement', 'while_statement', 'enhanced_for_statement', 'do_statement'])

    @evo.metric('Exception statements', aggregate='sum', categorical=True)
    def exception(commit: ParsedCommit):
        return commit.find_node_types(['try_statement', 'throw_statement'])

    @evo.metric('Comments', aggregate='sum', categorical=True)
    def comments(commit: ParsedCommit):
        return commit.find_node_types(['block_comment', 'line_comment'])