import asyncio
import logging
from functools import partial

import pytest
from aiohttp import web, ClientSession
from aiohttp.client_reqrep import ClientRequest
from aiohttp.connector import TCPConnector
from aiohttp.helpers import sentinel
from aiohttp.test_utils import BaseTestServer
from aiohttp.web_response import StreamResponse
from aiohttp.web_runner import ServerRunner
from aiohttp.web_server import Server

from aresponses.utils import _text_matches_pattern, ANY

logger = logging.getLogger(__name__)


class AresponsesAssertionError(AssertionError):
    pass


class UnmatchedRequest(AresponsesAssertionError):
    pass


class UnusedResponses(AresponsesAssertionError):
    pass


class IncorrectRequestOrder(AresponsesAssertionError):
    pass


class RawResponse(StreamResponse):
    """
    Allow complete control over the response

    Useful for mocking invalid responses
    """

    def __init__(self, body):
        super().__init__()
        self._body = body

    async def _start(self, request, *_, **__):
        self._req = request
        self._keep_alive = False
        writer = self._payload_writer = request._payload_writer
        return writer

    async def write_eof(self, *_, **__):
        await super().write_eof(self._body)


class ResponsesMockServer(BaseTestServer):
    ANY = ANY
    Response = web.Response
    RawResponse = RawResponse

    def __init__(self, *, scheme=sentinel, host="127.0.0.1", **kwargs):
        self._responses = []
        self._host_patterns = set()
        self._exception = None
        self._unmatched_requests = []
        self._first_unordered_request = None
        self._request_count = 0
        self.calls = []
        super().__init__(scheme=scheme, host=host, **kwargs)

    async def _make_runner(self, debug=True, **kwargs):
        srv = Server(self._handler, loop=self._loop, debug=True, **kwargs)
        return ServerRunner(srv, debug=debug, **kwargs)

    async def _close_hook(self):
        return

    async def _handler(self, request):
        self._request_count += 1
        self.calls.append(request)
        return await self._find_response(request)

    def add(self, host, path=ANY, method=ANY, response="", *, body_match=ANY, match_querystring=False):
        if isinstance(host, str):
            host = host.lower()

        if isinstance(method, str):
            method = method.lower()

        self._host_patterns.add(host)
        self._responses.append((host, path, method, body_match, response, match_querystring))

    def _host_matches(self, match_host):
        match_host = match_host.lower()
        for host_pattern in self._host_patterns:
            if _text_matches_pattern(host_pattern, match_host):
                return True

        return False

    async def _find_response(self, request):
        host, path, path_qs, method = request.host, request.path, request.path_qs, request.method
        logger.info(f"Looking for match for {host} {path} {method}")  # noqa
        i = -1
        for host_pattern, path_pattern, method_pattern, body_pattern, response, match_querystring in self._responses:
            i += 1
            if i > 0 and self._first_unordered_request is None:
                self._first_unordered_request = self._request_count

            path_to_match = path_qs if match_querystring else path

            if not _text_matches_pattern(host_pattern, host):
                continue

            if not _text_matches_pattern(path_pattern, path_to_match):
                continue

            if not _text_matches_pattern(method_pattern, method.lower()):
                continue

            if body_pattern != ANY:
                if not _text_matches_pattern(body_pattern, await request.text()):
                    continue

            del self._responses[i]

            if callable(response):
                if asyncio.iscoroutinefunction(response):
                    return await response(request)
                return response(request)

            if isinstance(response, str):
                return self.Response(body=response)

            return response

        self._unmatched_requests.append(request)

    async def passthrough(self, request):
        """Make non-mocked network request"""
        connector = TCPConnector()
        connector._resolve_host = partial(self._old_resolver_mock, connector)

        new_is_ssl = ClientRequest.is_ssl
        ClientRequest.is_ssl = self._old_is_ssl
        try:
            original_request = request.clone(scheme="https" if request.headers["AResponsesIsSSL"] else "http")

            headers = {k: v for k, v in request.headers.items() if k != "AResponsesIsSSL"}

            async with ClientSession(connector=connector) as session:
                async with getattr(session, request.method.lower())(original_request.url, headers=headers, data=(await request.read())) as r:
                    headers = {k: v for k, v in r.headers.items() if k.lower() == "content-type"}
                    data = await r.read()
                    response = self.Response(body=data, status=r.status, headers=headers)
                    return response
        finally:
            ClientRequest.is_ssl = new_is_ssl

    async def __aenter__(self) -> "ResponsesMockServer":
        await self.start_server(loop=self._loop)

        self._old_resolver_mock = TCPConnector._resolve_host

        async def _resolver_mock(_self, host, port, traces=None):
            return [{"hostname": host, "host": "127.0.0.1", "port": self.port, "family": _self._family, "proto": 0, "flags": 0}]

        TCPConnector._resolve_host = _resolver_mock

        self._old_is_ssl = ClientRequest.is_ssl

        def new_is_ssl(_self):
            return False

        ClientRequest.is_ssl = new_is_ssl

        # store whether a request was an SSL request in the `AResponsesIsSSL` header
        self._old_init = ClientRequest.__init__

        def new_init(_self, *largs, **kwargs):
            self._old_init(_self, *largs, **kwargs)

            is_ssl = "1" if self._old_is_ssl(_self) else ""
            _self.update_headers({**_self.headers, "AResponsesIsSSL": is_ssl})

        ClientRequest.__init__ = new_init

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        TCPConnector._resolve_host = self._old_resolver_mock
        ClientRequest.is_ssl = self._old_is_ssl

        await self.close()

    def assert_no_unused_responses(self):
        if self._responses:
            host, path, method, body_pattern, response, match_querystring = self._responses[0]
            raise UnusedResponses(f"Unused Response. host={host} path={path} method={method} body={body_pattern} match_querystring={match_querystring}")

    def assert_called_in_order(self):
        if self._first_unordered_request is not None:
            raise IncorrectRequestOrder(f"Request {self._first_unordered_request} was out of order")

    def assert_all_requests_matched(self):
        if self._unmatched_requests:
            request = self._unmatched_requests[0]
            raise UnmatchedRequest(f"No match found for request: {request.method} {request.host} {request.path}")

    def assert_plan_strictly_followed(self):
        self.assert_no_unused_responses()
        self.assert_called_in_order()
        self.assert_all_requests_matched()


@pytest.fixture
async def aresponses(event_loop) -> ResponsesMockServer:
    async with ResponsesMockServer(loop=event_loop) as server:
        yield server
