import aiohttp
import pytest

import aresponses


# example test in readme.md
@pytest.mark.asyncio
async def test_foo(aresponses):
    # text as response (defaults to status 200 response)
    aresponses.add("foo.com", "/", "get", "hi there!!")

    # custom status code response
    aresponses.add("foo.com", "/", "get", aresponses.Response(text="error", status=500))

    # passthrough response (makes an actual network call)
    aresponses.add("httpstat.us", "/200", "get", aresponses.passthrough)

    # custom handler response
    def my_handler(request):
        return aresponses.Response(status=200, text=str(request.url))

    aresponses.add("foo.com", "/", "get", my_handler)

    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            assert text == "hi there!!"

        async with session.get(url) as response:
            text = await response.text()
            assert text == "error"
            assert response.status == 500

        async with session.get("https://httpstat.us/200") as response:
            text = await response.text()
        assert text == "200 OK"

        async with session.get(url) as response:
            text = await response.text()
            assert text == "http://foo.com/"


@pytest.mark.asyncio
async def test_fixture(aresponses):
    aresponses.add("foo.com", "/", "get", aresponses.Response(text="hi"))

    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
async def test_fixture_body_json(aresponses):
    aresponses.add("foo.com", "/", "post", aresponses.Response(text="hi"), body={"a": 1})

    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"a": 1}) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
@pytest.mark.xfail(reason="json body not matched, remove to see fail message")
async def test_fixture_body_json_failed(aresponses):
    aresponses.add("foo.com", "/", "post", aresponses.Response(text="hi"), body={"a": 2})

    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"a": 1}) as _:
            pass


@pytest.mark.asyncio
async def test_fixture_body_text(aresponses):
    aresponses.add("foo.com", "/", "post", aresponses.Response(text="hi"), body='{"a": 1}')

    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"a": 1}) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
async def test_https(aresponses):
    aresponses.add("foo.com", "/", "get", aresponses.Response(text="hi"))

    url = "https://foo.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
async def test_context_manager(event_loop):
    async with aresponses.ResponsesMockServer(loop=event_loop) as arsps:
        arsps.add("foo.com", "/", "get", aresponses.Response(text="hi"))

        url = "http://foo.com"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
        assert text == "hi"


@pytest.mark.asyncio
async def test_bad_redirect(aresponses):
    aresponses.add("foo.com", "/", "get", aresponses.Response(text="hi", status=301))
    url = "http://foo.com"
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        await response.text()


@pytest.mark.asyncio
async def test_regex(aresponses):
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.Response(text="hi"))
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.Response(text="there"))

    async with aiohttp.ClientSession() as session:
        async with session.get("http://foo.com") as response:
            text = await response.text()
            assert text == "hi"

        async with session.get("http://bar.com") as response:
            text = await response.text()
            assert text == "there"


@pytest.mark.asyncio
async def test_callable(aresponses):
    def handler(request):
        return aresponses.Response(body=request.host)

    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, handler)
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, handler)

    async with aiohttp.ClientSession() as session:
        async with session.get("http://foo.com") as response:
            text = await response.text()
            assert text == "foo.com"

        async with session.get("http://bar.com") as response:
            text = await response.text()
            assert text == "bar.com"


@pytest.mark.asyncio
async def test_raw_response(aresponses):
    raw_response = b"""HTTP/1.1 200 OK\r
Date: Tue, 26 Dec 2017 05:47:50 GMT
\r
<html><body><h1>It works!</h1></body></html>
"""
    aresponses.add(aresponses.ANY, aresponses.ANY, aresponses.ANY, aresponses.RawResponse(raw_response))

    async with aiohttp.ClientSession() as session:
        async with session.get("http://foo.com") as response:
            text = await response.text()
            assert "It works!" in text


@pytest.mark.asyncio
async def test_querystring(aresponses):
    aresponses.add("foo.com", "/path", "get", aresponses.Response(text="hi"))

    url = "http://foo.com/path?reply=42"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "hi"

    aresponses.add("foo.com", "/path2?reply=42", "get", aresponses.Response(text="hi"), match_querystring=True)

    url = "http://foo.com/path2?reply=42"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
async def test_querystring_not_match(aresponses):
    aresponses.add("foo.com", "/path", "get", aresponses.Response(text="hi"), match_querystring=True)
    aresponses.add("foo.com", aresponses.ANY, "get", aresponses.Response(text="miss"), match_querystring=True)
    aresponses.add("foo.com", aresponses.ANY, "get", aresponses.Response(text="miss"), match_querystring=True)

    url = "http://foo.com/path?reply=42"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "miss"

    url = "http://foo.com/path?reply=43"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "miss"

    url = "http://foo.com/path"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "hi"


@pytest.mark.asyncio
async def test_passthrough(aresponses):
    aresponses.add("httpstat.us", "/200", "get", aresponses.passthrough)

    url = "https://httpstat.us/200"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
    assert text == "200 OK"
