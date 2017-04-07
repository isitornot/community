from sanic import Blueprint, exceptions
from sanic.views import HTTPMethodView
from sanic_jinja2 import SanicJinja2
from isitornot.auth.jwt_auth import unpack_auth


blueprint_rest_v1 = Blueprint('communities_v1', url_prefix='/v1')
blueprint_rest_v1.middleware('request')(unpack_auth)
jinja = SanicJinja2()


@blueprint_rest_v1.listener('after_server_start')
async def setup_jinja(app, loop):
    jinja.init_app(app)


class CommunityView(HTTPMethodView):
    async def get(self, request):
        raise exceptions.SanicException("GET not implemented", status_code=501)

    async def post(self, request):
        raise exceptions.SanicException("POST not implemented", status_code=501)


blueprint_rest_v1.add_route(CommunityView.as_view(), '/communities')
