# from gitevo.model import GitEvoResult


# class TableReport:

#     DATE_COLUMN_NAME = 'date'
    
#     def __init__(self, result: GitEvoResult):
#         self.metric_names = result.metric_names
#         self.metric_dates = result.metric_dates
#         self.evolutions = result.metric_evolutions()
    
#     def generate_table(self) -> list[list[str]]:
#         header = self._header()
#         t_values = self.transpose_matrix(self._values())
#         assert len(header) == len(t_values[0])
#         t_values.insert(0, header)
#         return t_values
    
#     def generate_table2(self) -> list[list[str]]:
#         return self.transpose_matrix(self.generate_table())

#     def transpose_matrix(self, matrix: list[list]) -> list[list]:
#         return [list(row) for row in zip(*matrix)]
    
#     def _header(self) -> list[str]:
#         return [self.DATE_COLUMN_NAME] + self.metric_names
    
#     def _values(self) -> list[list[str]]:
#         values = [evo.values_as_str for evo in self.evolutions]
#         values.insert(0, self.metric_dates)
#         return values