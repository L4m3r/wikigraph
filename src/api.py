from aiohttp import web
from aiohttp.web import Request
import wiki

routes = web.RouteTableDef()


@routes.get('/graph/{title}')
async def send_graph(request: Request):
    g = await wiki.Graph.create(request.match_info['title'])

    return web.json_response(data=g.graph)


@routes.get('/search/{title}')
async def search(request: Request):
    title = request.match_info['title']
    
    return web.json_response({title: await wiki.search(title)})


app = web.Application()
app.add_routes(routes)
web.run_app(app)
