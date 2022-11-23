import redis
from typing import Optional
import logging

logger = logging.getLogger('wiki')

class Cache:

    def __init__(self, host: str, port: int, db: int) -> None:
        self.r = redis.Redis(host, port, db)

    def set_links(self, page: str, links: list[str]) -> None:
        self.r.set('page:' + page, '|'.join(links))
        logger.debug('Set %s links %s', page, ' '.join(links))

    def get_links(self, page: str) -> Optional[list[str]]:
        data = self.r.get('page:' + page)

        return None if data is None else data.decode('utf-8').split('|')
