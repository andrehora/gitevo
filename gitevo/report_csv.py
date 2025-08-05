import csv
import os
from gitevo.model import GitEvoResult


class TableReport:

    DATE_COLUMN_NAME = 'date'
    
    def __init__(self, result: GitEvoResult):
        self.report_filename = self._ensure_filename(result)
        self.metric_names = result.metric_names
        self.metric_dates = result.metric_dates
        self.evolutions = result.metric_evolutions()

    def export_csv(self):
        data = self.generate_table()
        self._export_csv(data)
        return os.path.join(os.getcwd(), self.report_filename)
    
    def generate_table(self) -> list[list[str]]:
        header = self._header()
        t_values = self.transpose_matrix(self._values())
        assert len(header) == len(t_values[0])
        t_values.insert(0, header)
        return t_values
    
    def generate_table2(self) -> list[list[str]]:
        return self.transpose_matrix(self.generate_table())

    def transpose_matrix(self, matrix: list[list]) -> list[list]:
        return [list(row) for row in zip(*matrix)]
    
    def _ensure_filename(self, result: GitEvoResult) -> str:
        if result.report_filename is None:
            filename = f'report_{result.project_result.name}.csv'
            return filename
        return result.report_filename
    
    def _export_csv(self, data: list[list[str]]) -> None:
        with open(self.report_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    def _header(self) -> list[str]:
        return [self.DATE_COLUMN_NAME] + self.metric_names
    
    def _values(self) -> list[list[str]]:
        values = [evo.values_as_str for evo in self.evolutions]
        values.insert(0, self.metric_dates)
        return values