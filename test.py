import asyncio
import unittest

from aiohttp import (
    web,
)

from lowhaio import (
    HttpConnectionError,
    Pool,
    streamed,
    buffered,
)
from lowhaio_retry import (
    retry,
)


def async_test(func):
    def wrapper(*args, **kwargs):
        future = func(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestIntegration(unittest.TestCase):

    def add_async_cleanup(self, coroutine, *args):
        loop = asyncio.get_event_loop()
        self.addCleanup(loop.run_until_complete, coroutine(*args))

    @async_test
    async def test_http_retry_then_succeed(self):

        async def handle_post(_):
            return web.Response(text='the-response-data')

        app = web.Application()
        app.add_routes([
            web.post('/page', handle_post)
        ])
        runner = web.AppRunner(app)

        request, close = Pool()
        self.addCleanup(close)

        retriable_request = retry(request,
                                  exception_intervals=(
                                      (HttpConnectionError, (0, 1, 2)),
                                  ),
                                  )

        async def delayed_start():
            await asyncio.sleep(0.5)
            await runner.setup()
            self.add_async_cleanup(runner.cleanup)
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()

        asyncio.ensure_future(delayed_start())
        _, _, body = await retriable_request(
            b'POST', 'http://localhost:8080/page',
            body=streamed(b'some-data'),
            headers=((b'content-length', b'9'),)
        )

        self.assertEqual(b'the-response-data', await buffered(body))

    @async_test
    async def test_http_retry_fail_eventually_(self):

        request, close = Pool()
        self.addCleanup(close)

        retriable_request = retry(request,
                                  exception_intervals=(
                                      (HttpConnectionError, (0, 1)),
                                  ),
                                  )
        with self.assertRaises(HttpConnectionError):
            await retriable_request(b'GET', 'http://localhost:8080/page')

    @async_test
    async def test_http_retry_fail_immediately_a(self):

        request, close = Pool()
        self.addCleanup(close)

        retriable_request = retry(request,
                                  exception_intervals=(
                                      (HttpConnectionError, ()),
                                  ),
                                  )
        with self.assertRaises(HttpConnectionError):
            await retriable_request(b'GET', 'http://localhost:8080/page')

    @async_test
    async def test_http_retry_fail_immediately_b(self):

        request, close = Pool()
        self.addCleanup(close)

        retriable_request = retry(request,
                                  exception_intervals=(),
                                  )
        with self.assertRaises(HttpConnectionError):
            await retriable_request(b'GET', 'http://localhost:8080/page')
