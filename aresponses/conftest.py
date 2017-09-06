import re

import pytest
from aiohttp.client_reqrep import ClientRequest
from aiohttp.connector import TCPConnector
from aiohttp.helpers import sentinel
from aiohttp.test_utils import BaseTestServer
from aiohttp.web_server import Server


def _text_matches_pattern(pattern, text):
    if isinstance(pattern, str):
        if pattern == text:
            return True
    elif isinstance(pattern, re._pattern_type):
        if pattern.search(text):
            return True
    return False


class ResponsesTestServer(BaseTestServer):
    def __init__(self, *, scheme=sentinel, host='127.0.0.1', **kwargs):
        self._responses = []
        self._host_patterns = set()
        self._exception = None
        super().__init__(scheme=scheme, host=host, **kwargs)

    async def _make_factory(self, debug=True, **kwargs):
        self.handler = Server(self._handler, loop=self._loop, debug=True, **kwargs)
        return self.handler

    async def _close_hook(self):
        return

    async def _handler(self, request):
        return self._find_response(request.host, request.path, request.method)

    def add(self, host_pattern, path_pattern, method_pattern, response):
        if isinstance(host_pattern, str):
            host_pattern = host_pattern.lower()

        if isinstance(method_pattern, str):
            method_pattern = method_pattern.lower()

        self._host_patterns.add(host_pattern)
        self._responses.append((host_pattern, path_pattern, method_pattern, response))

    def _host_matches(self, match_host):
        match_host = match_host.lower()
        for host_pattern in self._host_patterns:
            if _text_matches_pattern(host_pattern, match_host):
                return True

        return False

    def _find_response(self, host, path, method):
        i = 0
        for host_pattern, path_pattern, method_pattern, response in self._responses:
            if _text_matches_pattern(host_pattern, host):
                if _text_matches_pattern(path_pattern, path):
                    if _text_matches_pattern(method_pattern, method.lower()):
                        del self._responses[i]
                        return response
            i += 1
        self._exception = Exception("No Match found")
        raise self._exception  # noqa


@pytest.yield_fixture
async def aresponses(event_loop):
    server = ResponsesTestServer()
    await server.start_server(event_loop)

    old_resolver_mock = TCPConnector._resolve_host

    async def _resolver_mock(self, host, port):
        return [{
            'hostname': host, 'host': '127.0.0.1', 'port': server.port,
            'family': self._family, 'proto': 0, 'flags': 0
        }]

    TCPConnector._resolve_host = _resolver_mock

    old_update_host = ClientRequest.update_host

    def new_update_host(self, *args, **kwargs):
        val = old_update_host(self, *args, **kwargs)
        self.ssl = False
        return val

    ClientRequest.update_host = new_update_host
    yield server

    TCPConnector._resolve_host = old_resolver_mock
    ClientRequest.update_host = old_update_host

    await server.close()
    if server._exception:
        raise server._exception  # noqa
