from gitevo import GitEvo, ParsedCommit
from gitevo.reports.fastapi import FastAPICommit


remote = 'https://github.com/fastapi/full-stack-fastapi-template'
# remote = 'https://github.com/fastapi/fastapi'
# remote = 'https://github.com/Netflix/dispatch'

evo = GitEvo(repo=remote, extension='.py')

@evo.before(file_extension='.py')
def before(commit: ParsedCommit):
    return FastAPICommit(commit)

@evo.metric('Number of endpoints', aggregate='sum', show_version_chart=False)
def endpoints(fastapi: FastAPICommit):
    return len(fastapi.endpoints())

@evo.metric('Endpoints: mean LOC', aggregate='mean', show_version_chart=False)
def mean_parameters(fastapi: FastAPICommit):
    
    endpoints = fastapi.endpoints()
    number_of_endpoints = len(endpoints)
    if number_of_endpoints == 0:
        return 0
    
    sum_loc = sum([endpoint.function.loc for endpoint in endpoints])
    return round(sum_loc/number_of_endpoints, 2)

@evo.metric('Endpoints: HTTP methods', categorical=True, aggregate='sum', top_n=5)
def http_method(fastapi: FastAPICommit):
    return [endpoint.decorator.http_method for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: sync vs. async', categorical=True, aggregate='sum')
def sync_async(fastapi: FastAPICommit):
    return [endpoint.function.sync_async() for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: return type in function?', categorical=True, aggregate='sum')
def has_return_type(fastapi: FastAPICommit):
    return [str(endpoint.function.has_return_type()) for endpoint in fastapi.endpoints()]

@evo.metric('Endpoints: typed vs. untyped parameters', categorical=True, aggregate='sum', show_version_chart=False)
def typed_untyped(fastapi: FastAPICommit):
    return [typed_untyped for endpoint in fastapi.endpoints() for typed_untyped in endpoint.function.typed_untyped()]

@evo.metric('Endpoints: default parameters?', categorical=True, aggregate='sum')
def defaults(fastapi: FastAPICommit):
    return [str(has_default) for endpoint in fastapi.endpoints() for has_default in endpoint.function.defaults()]

@evo.metric('Endpoints: common parameter names', categorical=True, aggregate='sum', version_chart_type='hbar', top_n=5)
def parameter_names(fastapi: FastAPICommit):
    return [param_name for endpoint in fastapi.endpoints() for param_name in endpoint.function.parameter_names()]

@evo.metric('Endpoints: common parameter types', categorical=True, aggregate='sum', version_chart_type='hbar', top_n=5)
def parameter_types(fastapi: FastAPICommit):
    return [param_type for endpoint in fastapi.endpoints() for param_type in endpoint.function.parameter_types()]

@evo.metric('Endpoints: mean number of parameters', aggregate='mean', show_version_chart=False)
def mean_parameters(fastapi: FastAPICommit):
    
    endpoints = fastapi.endpoints()
    number_of_endpoints = len(endpoints)
    if number_of_endpoints == 0:
        return 0
    
    sum_of_parameters = sum([len(endpoint.function.parameters) for endpoint in endpoints])
    return round(sum_of_parameters/number_of_endpoints, 2)

@evo.metric('Security imports', categorical=True, aggregate='sum', version_chart_type='hbar', top_n=5)
def security_imports(fastapi: FastAPICommit):
    return fastapi.security_imports()

@evo.metric('Response imports', categorical=True, aggregate='sum', version_chart_type='hbar', show_version_chart=False, top_n=5)
def response_imports(fastapi: FastAPICommit):
    return fastapi.response_imports()

@evo.metric('FastAPI imports', aggregate='sum', show_version_chart=False)
def fastapi_imports(fastapi: FastAPICommit):
    return len(fastapi.fastapi_imports())

@evo.metric('APIRouter imports', aggregate='sum', show_version_chart=False)
def apirouter_imports(fastapi: FastAPICommit):
    return len(fastapi.apirouter_imports())

@evo.metric('UploadFile imports', aggregate='sum', show_version_chart=False)
def upload_file_imports(fastapi: FastAPICommit):
    return len(fastapi.upload_file_imports())

@evo.metric('BackgroundTasks imports', aggregate='sum', show_version_chart=False)
def background_tasks_imports(fastapi: FastAPICommit):
    return len(fastapi.background_tasks_imports())

@evo.metric('WebSocket imports', aggregate='sum', show_version_chart=False)
def websocket_imports(fastapi: FastAPICommit):
    return len(fastapi.websocket_imports())

evo.run()
