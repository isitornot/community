from .models import Community, Tag
import os.path
from pony.orm import db_session, ObjectNotFound, commit
from sanic import Blueprint, exceptions, response
from sanic.views import HTTPMethodView
from sanic_openapi import doc
from isitornot.auth.jwt_auth import unpack_auth
from isitornot.rest_utils import validate_json


blueprint_rest_v1 = Blueprint('communities_v1', url_prefix='/v1')
blueprint_rest_v1.middleware('request')(unpack_auth)


class CommunityView(HTTPMethodView):
    def __init__(self):
        super().__init__()

    async def options(self, _):
        return response.text('')

    @doc.summary("Retrieve a list of all communities. Optional 'limit' query parameter will limit the number of returned communities.")
    @doc.produces(doc.List(Community))
    async def get(self, request):
        with db_session:
            rval = []
            query = Community.select()
            if 'limit' in request.args:
                query = query.limit(int(request.args['limit'][0]))
            for c in query:
                rval.append({
                    'id': c.id,
                    'slug': c.slug,
                    'name': c.name if c.name is not "" else c.slug,
                    'icon': c.icon
                })
            return response.json({'communities': rval})

    @doc.summary("Create a new community.")
    @validate_json(schema_file=os.path.join(os.path.dirname(__file__), "..", "..", "schema", "community_detail_v1.json"))
    async def post(self, request):
        if "id" in request.json:
            raise exceptions.SanicException("ID should not be specified with POST", status_code=409)
        with db_session:
            if Community.exists(slug=request.json['slug']):
                raise exceptions.SanicException("Slug already exists", status_code=409)
            c = Community(slug=request.json['slug'],
                          name=request.json.get('name', ""),
                          description=request.json.get('description', ""),
                          icon=request.json.get('icon', ""),
                          owner=request.json['owner'])
            for tag_name in request.json.get('tags', []):
                try:
                    tag = Tag[tag_name]
                except ObjectNotFound:
                    tag = Tag(tag=tag_name)
                c.tags.add(tag)
            commit()
            return response.json(c.to_dict(),
                                 status=201,
                                 headers={"Location": request.app.url_for("communities_v1.CommunityDetailView",
                                                                          id=c.id)})


class CommunityDetailView(HTTPMethodView):
    @doc.summary("Access community details by id")
    @doc.produces(Community)
    async def get(self, _, id: str):
        with db_session:
            try:
                c = Community[id]
                return response.json(c.to_dict())
            except (ObjectNotFound, ValueError) as _:
                pass  # try it as a slug
            try:
                c = Community.get(slug=id)
                if c is None:
                    raise exceptions.NotFound("Community {} not found".format(id))
                return response.json(c.to_dict())
            except ObjectNotFound:
                raise exceptions.NotFound("Community {} not found".format(id))

    @doc.summary("Modify an existing community.")
    async def patch(self, request, id):
        with db_session:
            try:
                c = Community[id]
                if 'slug' in request.json:
                    c.slug = request.json['slug']
                if 'name' in request.json:
                    c.name = request.json['name']
                if 'description' in request.json:
                    c.description = request.json['description']
                if 'icon' in request.json:
                    c.icon = request.json['icon']
                if 'owner' in request.json:
                    c.owner = request.json['owner']
                if 'tags' in request.json:
                    c.tags.clear()
                    for tag_name in request.json['tags']:
                        try:
                            tag = Tag[tag_name]
                        except ObjectNotFound:
                            tag = Tag(tag=tag_name)
                        c.tags.add(tag)
                commit()
                return response.json(c.to_dict())
            except ObjectNotFound:
                raise exceptions.NotFound("Community {} not found".format(id))

    @doc.summary("Delete a community")
    async def delete(self, _, id):
        with db_session:
            try:
                c = Community[id]
                c.delete()
                commit()
            except ObjectNotFound:
                raise exceptions.NotFound("Community {} not found".format(id))
            return response.text('', status=204)



blueprint_rest_v1.add_route(CommunityView.as_view(), '/communities')
blueprint_rest_v1.add_route(CommunityDetailView.as_view(), '/communities/<id>')
