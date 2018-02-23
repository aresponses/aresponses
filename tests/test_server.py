import aiohttp
import pytest

import aresponses


@pytest.mark.asyncio
async def test_fixture(aresponses):
    aresponses.add('foo.com', '/', 'get', aresponses.Response(text='hi'))

    url = 'http://foo.com'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == 'hi'


@pytest.mark.asyncio
async def test_https(aresponses):
    aresponses.add('foo.com', '/', 'get', aresponses.Response(text='hi'))

    url = 'https://foo.com'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == 'hi'


@pytest.mark.asyncio
async def test_context_manager(event_loop):
    async with aresponses.ResponsesMockServer(loop=event_loop) as arsps:
        arsps.add('foo.com', '/', 'get', aresponses.Response(text='hi'))

        url = 'http://foo.com'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
        assert text == 'hi'


@pytest.mark.asyncio
async def test_bad_redirect(aresponses):
    aresponses.add('foo.com', '/', 'get', aresponses.Response(text='hi', status=301))
    url = 'http://foo.com'
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        await response.text()


@pytest.mark.asyncio
async def test_regex(aresponses):
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.Response(text='hi'))
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.Response(text='there'))

    async with aiohttp.ClientSession() as session:
        async with session.get('http://foo.com') as response:
            text = await response.text()
            assert text == 'hi'

        async with session.get('http://bar.com') as response:
            text = await response.text()
            assert text == 'there'


@pytest.mark.asyncio
async def test_callable(aresponses):
    def handler(request):
        return aresponses.Response(body=request.host)

    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, handler)
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, handler)

    async with aiohttp.ClientSession() as session:
        async with session.get('http://foo.com') as response:
            text = await response.text()
            assert text == 'foo.com'

        async with session.get('http://bar.com') as response:
            text = await response.text()
            assert text == 'bar.com'


@pytest.mark.asyncio
async def test_raw_response(aresponses):
    raw_response = b"""HTTP/1.1 200 OK\r
Date: Tue, 26 Dec 2017 05:47:50 GMT
\r
<html><body><h1>It works!</h1></body></html>
"""
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.RawResponse(raw_response))

    async with aiohttp.ClientSession() as session:
        async with session.get('http://foo.com') as response:
            text = await response.text()
            assert 'It works!' in text
