from fastapi import FastAPI, Depends, templating, responses, Request, staticfiles
from fastapi.middleware.cors import CORSMiddleware

from app.tag_meta import tags_metadata
from app.auth import auth_router
from app.auth.auth_utils import get_current_user
from app.routers import users, teams, projects, columns, tasks


def create_application() -> FastAPI:
    application = FastAPI(
        title='Asana FastAPI',
        openapi_tags=tags_metadata,
        description='FastAPI Python server for an Asana clone')
    application.mount(
        path='/static', name='static',
        app=staticfiles.StaticFiles(directory='app/static'))

    application.add_middleware(
        middleware_class=CORSMiddleware,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        allow_origins=[
            'http://localhost:3000',   # TODO: remove
            'https://localhost:3000',  # TODO: remove
            'http://react.colerutledge.dev',
            'https://react.colerutledge.dev'])

    application.include_router(auth_router.router, tags=['Auth'])
    application.include_router(users.router, tags=['Users'], prefix='/users')

    protected_routers = [
        (teams.router, 'Teams', '/teams'),
        (projects.router, 'Projects', '/projects'),
        (columns.router, 'Columns', '/columns'),
        (tasks.router, 'Tasks', '/tasks')]
    for router, tag, prefix in protected_routers:
        application.include_router(
            router=router, tags=[tag], prefix=prefix,
            dependencies=[Depends(get_current_user)])

    return application


app = create_application()


@app.on_event('startup')
def startup_event():
    import os
    from logging.config import dictConfig
    from app import config

    os.makedirs('logs', exist_ok=True)
    dictConfig(config.LOGGING_CONFIG)


templates = templating.Jinja2Templates(directory='app/templates')


@app.get('/', response_class=responses.HTMLResponse)
async def user_login(request: Request):
    return templates.TemplateResponse(
        'index.html', {'request': request, 'request_headers': request._headers._list})


# @app.get('/items/{id}', response_class=responses.HTMLResponse)
# async def read_item(request: Request, id: str):
#     return templates.TemplateResponse('item.html', {'request': request, 'id': id})
