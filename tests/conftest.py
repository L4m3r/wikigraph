import pytest
import redis
from src import cache

HOST = '172.19.0.2'
PORT = 6379
DB = 0
PREFIX = 'test:'


def delete_test_keys():
    r = redis.Redis(HOST, PORT, DB)
    keys = [key.decode('utf-8') for key in r.keys('test:*')]
    if len(keys) == 0:
        return
    deleted = r.delete(*keys)
    if len(keys) != deleted:
        raise Exception("Something went wrong")


@pytest.fixture(scope="session")
def cache_setup():
    delete_test_keys()

    c = cache.Cache(HOST, PORT, DB)
    c.prefix = PREFIX
    yield c

    delete_test_keys()
