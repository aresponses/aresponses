import aiohttp
import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_bad_redirect(event_loop, aresponses):
    aresponses.add('foo.com', '/', 'get', web.Response(text='hi', status=301))

    url = 'http://foo.com'
    async with aiohttp.ClientSession(loop=event_loop) as session:
        async with session.get(url) as response:
            text = await response.text()

    print(text)
