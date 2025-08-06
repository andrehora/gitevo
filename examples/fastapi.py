from gitevo import GitEvo, ParsedCommit
from gitevo.reports.fastapi import FastAPICommit


remote = 'https://github.com/fastapi/full-stack-fastapi-template'
# remote = 'https://github.com/fastapi/fastapi'
# remote = 'https://github.com/Netflix/dispatch'

evo = GitEvo(repo=remote, extension='.py')

@evo.metric('Number of endpoints', show_version_chart=False)
def endpoints(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.endpoints())

@evo.metric('Endpoints: mean LOC', show_version_chart=False)
def mean_parameters(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    
    endpoints = fastapi.endpoints()
    number_of_endpoints = len(endpoints)
    if number_of_endpoints == 0:
        return 0
    
    sum_loc = sum([endpoint.function.loc for endpoint in endpoints])
    return round(sum_loc/number_of_endpoints, 2)

@evo.metric('Endpoints: HTTP methods', categorical=True, top_n=5)
def http_method(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [endpoint.decorator.http_method for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: sync vs. async', categorical=True)
def sync_async(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [endpoint.function.sync_async() for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: return type in function?', categorical=True)
def has_return_type(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [str(endpoint.function.has_return_type()) for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: typed vs. untyped parameters', categorical=True, show_version_chart=False)
def typed_untyped(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [typed_untyped for endpoint in fastapi.endpoints() for typed_untyped in endpoint.function.typed_untyped()]

@evo.metric('Endpoints: default parameters?', categorical=True)
def defaults(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [str(has_default) for endpoint in fastapi.endpoints() for has_default in endpoint.function.defaults()]

@evo.metric('Endpoints: common parameter names', categorical=True, version_chart_type='hbar', top_n=5)
def parameter_names(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [param_name for endpoint in fastapi.endpoints() for param_name in endpoint.function.parameter_names()]

@evo.metric('Endpoints: common parameter types', categorical=True, version_chart_type='hbar', top_n=5)
def parameter_types(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return [param_type for endpoint in fastapi.endpoints() for param_type in endpoint.function.parameter_types()]

@evo.metric('Endpoints: mean number of parameters', show_version_chart=False)
def mean_parameters(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)

    endpoints = fastapi.endpoints()
    number_of_endpoints = len(endpoints)
    if number_of_endpoints == 0:
        return 0
    
    sum_of_parameters = sum([len(endpoint.function.parameters) for endpoint in endpoints])
    return round(sum_of_parameters/number_of_endpoints, 2)

@evo.metric('Security imports', categorical=True, version_chart_type='hbar', top_n=5)
def security_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return fastapi.security_imports()

@evo.metric('Response imports', categorical=True, version_chart_type='hbar', show_version_chart=False, top_n=5)
def response_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return fastapi.response_imports()

@evo.metric('FastAPI imports', show_version_chart=False)
def fastapi_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.fastapi_imports())

@evo.metric('APIRouter imports', show_version_chart=False)
def apirouter_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.apirouter_imports())

@evo.metric('UploadFile imports', show_version_chart=False)
def upload_file_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.upload_file_imports())

@evo.metric('BackgroundTasks imports', show_version_chart=False)
def background_tasks_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.background_tasks_imports())

@evo.metric('WebSocket imports', show_version_chart=False)
def websocket_imports(commit: ParsedCommit):
    fastapi = FastAPICommit(commit)
    return len(fastapi.websocket_imports())

evo.run()
