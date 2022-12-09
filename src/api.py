import logging

from aiohttp import web
from aiohttp.web import Request

import wiki
from requestClasses import GraphRequest, SearchRequest

logger = logging.getLogger('wiki')


@web.middleware
async def json_middleware(request: Request, handler):
    try:
        data = dict(request.rel_url.query)
    except Exception as e:
        logger.error('JsonMiddlewareError: %s', e)
        return web.json_response({'Error': 'Unknown error'})

    request.data = data
    return await handler(request)


routes = web.RouteTableDef()


# TODO: refactor copied code
@routes.get('/graph')
async def send_graph(request: Request):
    try:
        request.data = GraphRequest(**request.data)
    except AttributeError as e:
        logger.error('AttributeError %s', e)
        return web.json_response(data={"Error": "Invalid json format"})

    g = await wiki.Graph.create(request.data.title, request.data.depth)
    resp = g.graph
    return web.json_response(data=resp)


@routes.get('/search')
async def search(request: Request):
    try:
        request.data = SearchRequest(**request.data)
    except AttributeError as e:
        logger.error('AttributeError %s', e)
        return web.json_response(data={"Error": "Invalid json format"})

    resp = await wiki.search(request.data.title, request.data.limit)
    return web.json_response(data={"search": resp})


app = web.Application(middlewares=[json_middleware])
app.add_routes(routes)
web.run_app(app)
