import asyncio
import logging
import aiohttp
import lxml
from time import time
from bs4 import BeautifulSoup
from cache import Cache
import json

FORMAT = '%(asctime)s [%(levelname)s] - %(name)s: "%(message)s" (%(filename)s:%(lineno)d)'

logging.basicConfig(format=FORMAT)

logger = logging.getLogger('wiki')
logger.setLevel(logging.DEBUG)

BASE_URL = "https://ru.wikipedia.org/wiki/"
API_URL = "http://ru.wikipedia.org/w/api.php"

headers = {
    'User-Agent': 'wikipedia (https://github.com/goldsmith/Wikipedia/)'
}

MAX_WORKERS = 4

class Graph:
    
    def __init__(self, title: str, depth = 2) -> None:
        self.title = title
        self.depth = depth
        self.cache = Cache('redis', 6379, 0)
        self.g: dict[str, list[str]] = {}
        self.worker_queue = asyncio.Queue()
        self.task_queue = asyncio.Queue()
        
    @classmethod
    async def create(cls, title: str, depth = 2):
        graph = Graph(title, depth)
        await graph.build()
        
        if hasattr(graph, 'session'):
            await graph.session.close()
        
        return graph

    async def build(self):
        curr = 1
        self.task_queue.put_nowait(self.title)
        workers = []
        
        while curr <= self.depth:
            
            while not self.task_queue.empty():
                self.worker_queue.put_nowait(self.task_queue.get_nowait())
            
            for _ in range(MAX_WORKERS):
                task = asyncio.create_task(
                    self.worker(self.worker_queue, self.task_queue))
                workers.append(task)
                
            await self.worker_queue.join()
            
            curr += 1
        
        for worker in workers:
            worker.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)
    
    async def worker(self, worker_queue: asyncio.Queue, task_queue: asyncio.Queue) -> list[str]:
        while True:
            page = await worker_queue.get()
            
            links = self.cache.get_links(page)
            # check in cache
            if links is None:
                links = await self.get_link(page)
                self.cache.set_links(page, links)
            
            for link in links:
                task_queue.put_nowait(link)
            
            self.g[page] = links
                
            worker_queue.task_done()

    async def get_link(self, page: str) -> list[str]:
        
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()

        async with self.session.get(BASE_URL + page, headers=headers) as resp:
            text = await resp.text()
            bs = BeautifulSoup(text, 'lxml')

            p = bs.find('div', id='mw-content-text') \
                  .find('div',class_='mw-parser-output') \
                  .find('p', recursive=False)

            data = set()

            for link in p.find_all("a", recursive=False):
                data.add(link['title'])

            logger.debug('Page: %s. Found %s links', page, len(data))
            
            return list(data)
    
    @property
    def graph(self):
        return self.g

# TODO error handeling
async def search(title: str, limit: int = 10) -> list[str]:
    async with aiohttp.ClientSession() as session:
        params = {
            'list': 'search',
            'srprop': '',
            'srlimit': limit,
            'srsearch': title,
            'action': 'query',
            'format': 'json'
        }
        async with session.get(API_URL, headers=headers, params=params) as resp:
            data = json.loads(await resp.text())
            return [r['title'] for r in data['query']['search']]


async def main():
    
    g = await Graph.create('Память', 2)
    #links = await get_links('Москва')
    print(g.graph)

if __name__ == '__main__':
    t = time()
    asyncio.get_event_loop().run_until_complete(main())

    # get_links("Объектно-ориентированное_программирование")

    print(time() - t)
    