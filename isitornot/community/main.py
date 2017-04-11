#!/usr/bin/env python


import os.path
from isitornot.db import PonyDatabase
from sanic import Sanic, response
from sanic_session import InMemorySessionInterface
from sanic_openapi import swagger_blueprint, openapi_blueprint
from sanic_jinja2 import SanicJinja2
try:
    from .views_rest_v1 import blueprint_rest_v1
    from . import models
except:
    from views_rest_v1 import blueprint_rest_v1
    import models


DEFAULT_CONFIG = {
    'AUTH0': {
        'CLIENT_SECRET': 'INVALID_SECRET',
        'CLIENT_ID': 'INVALID_CLIENT_ID',
        'REDIRECT_URL': 'http://localhost:9000/auth_callback',
        'DOMAIN': 'USER.auth0.com'
    },
    'DB_PROVIDER': 'sqlite',
    'DB_ARGS': [':memory:'],
    'DB_KARGS': {'create_db': True}
}


app = Sanic(__name__)
app.config.update(DEFAULT_CONFIG)
app.config.from_envvar('CONFIG_FILE')
app.static('/static', os.path.join(os.path.dirname(__file__), 'static'))
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
session_interface = InMemorySessionInterface()


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    if response:
        await session_interface.save(request, response)


app.blueprint(blueprint_rest_v1, url_prefix='/v1')
jinja = SanicJinja2(app)


@app.route("/")
def index(_):
    return response.redirect("/swagger/")


if __name__ == '__main__':
    from pony import orm
    #orm.sql_debug(True)
    db = PonyDatabase()
    db.bind(app.config['DB_PROVIDER'], *app.config['DB_ARGS'], **app.config['DB_KARGS'])
    db.generate_mapping(create_tables=True)
    app.run(host='0.0.0.0', port='9000', debug=True)
