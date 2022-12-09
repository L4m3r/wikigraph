from conftest import HOST, PORT, DB, PREFIX
import redis


def test_cache(cache_setup):
    page = 'test_cache'
    links = ['1', '2', '3']

    cache_setup.set_links(page, links)
    resp = cache_setup.get_links(page)

    assert links == resp


def test_get_links_of_not_existing_page(cache_setup):
    page = 'test_get_links_of_not_existing_page'

    resp = cache_setup.get_links(page)

    assert resp is None


def test_set_links(cache_setup):
    page = 'test_set_links'
    links = ['link1', 'link2', 'link3']

    cache_setup.set_links(page, links)

    r = redis.Redis(HOST, PORT, DB)
    resp = r.get(PREFIX + page).decode('utf-8')

    assert '|'.join(links) == resp


def test_get_links(cache_setup):
    page = 'test_get_links'
    links = ['link-1', 'link-2', 'link-3']

    cache_setup.set_links(page, links)
    resp = cache_setup.get_links(page)

    assert links == resp
