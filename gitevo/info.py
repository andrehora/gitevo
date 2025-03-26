class MetricInfo:
    
    def __init__(self, name: str, callback, file_extension: str, categorical: bool,
                 aggregate: str, group: str, version_chart_type: str, show_version_chart: bool,
                 top_n: int):
        
        self._name = name
        self.callback = callback
        self.file_extension = file_extension
        self.categorical = categorical
        self.aggregate = aggregate
        self._group = group
        self.version_chart_type = version_chart_type
        self.show_version_chart = show_version_chart
        self.top_n = top_n

    @property
    def name(self) -> str:
        if self._name is None:
            return self.callback.__name__
        return self._name.strip()
    
    @property
    def name_or_none_for_categorical(self) -> str | None:
        if self.categorical:
            return None
        return self.name
    
    @property
    def group(self) -> str:
        if self._group is None:
            return self.name
        return self._group.strip()
    
class BeforeCommitInfo:

    def __init__(self, file_extension: str, callback: callable):
        self.file_extension = file_extension
        self.callback = callback