"""Tests for streams.py."""

import gc
import os
import queue
import socket
import sys
import threading
import unittest
from unittest import mock
try:
    import ssl
except ImportError:
    ssl = None

import asyncio
from asyncio import test_utils


class StreamReaderTests(test_utils.TestCase):

    DATA = b'line1\nline2\nline3\n'

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.set_event_loop(self.loop)

    def tearDown(self):
        # just in case if we have transport close callbacks
        test_utils.run_briefly(self.loop)

        self.loop.close()
        gc.collect()
        super().tearDown()

    @mock.patch('asyncio.streams.events')
    def test_ctor_global_loop(self, m_events):
        stream = asyncio.StreamReader()
        self.assertIs(stream._loop, m_events.get_event_loop.return_value)

    def _basetest_open_connection(self, open_connection_fut):
        reader, writer = self.loop.run_until_complete(open_connection_fut)
        writer.write(b'GET / HTTP/1.0\r\n\r\n')
        f = reader.readline()
        data = self.loop.run_until_complete(f)
        self.assertEqual(data, b'HTTP/1.0 200 OK\r\n')
        f = reader.read()
        data = self.loop.run_until_complete(f)
        self.assertTrue(data.endswith(b'\r\n\r\nTest message'))
        writer.close()

    def test_open_connection(self):
        with test_utils.run_test_server() as httpd:
            conn_fut = asyncio.open_connection(*httpd.address,
                                               loop=self.loop)
            self._basetest_open_connection(conn_fut)

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    def test_open_unix_connection(self):
        with test_utils.run_test_unix_server() as httpd:
            conn_fut = asyncio.open_unix_connection(httpd.address,
                                                    loop=self.loop)
            self._basetest_open_connection(conn_fut)

    def _basetest_open_connection_no_loop_ssl(self, open_connection_fut):
        try:
            reader, writer = self.loop.run_until_complete(open_connection_fut)
        finally:
            asyncio.set_event_loop(None)
        writer.write(b'GET / HTTP/1.0\r\n\r\n')
        f = reader.read()
        data = self.loop.run_until_complete(f)
        self.assertTrue(data.endswith(b'\r\n\r\nTest message'))

        writer.close()

    @unittest.skipIf(ssl is None, 'No ssl module')
    def test_open_connection_no_loop_ssl(self):
        with test_utils.run_test_server(use_ssl=True) as httpd:
            conn_fut = asyncio.open_connection(
                *httpd.address,
                ssl=test_utils.dummy_ssl_context(),
                loop=self.loop)

            self._basetest_open_connection_no_loop_ssl(conn_fut)

    @unittest.skipIf(ssl is None, 'No ssl module')
    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    def test_open_unix_connection_no_loop_ssl(self):
        with test_utils.run_test_unix_server(use_ssl=True) as httpd:
            conn_fut = asyncio.open_unix_connection(
                httpd.address,
                ssl=test_utils.dummy_ssl_context(),
                server_hostname='',
                loop=self.loop)

            self._basetest_open_connection_no_loop_ssl(conn_fut)

    def _basetest_open_connection_error(self, open_connection_fut):
        reader, writer = self.loop.run_until_complete(open_connection_fut)
        writer._protocol.connection_lost(ZeroDivisionError())
        f = reader.read()
        with self.assertRaises(ZeroDivisionError):
            self.loop.run_until_complete(f)
        writer.close()
        test_utils.run_briefly(self.loop)

    def test_open_connection_error(self):
        with test_utils.run_test_server() as httpd:
            conn_fut = asyncio.open_connection(*httpd.address,
                                               loop=self.loop)
            self._basetest_open_connection_error(conn_fut)

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    def test_open_unix_connection_error(self):
        with test_utils.run_test_unix_server() as httpd:
            conn_fut = asyncio.open_unix_connection(httpd.address,
                                                    loop=self.loop)
            self._basetest_open_connection_error(conn_fut)

    def test_feed_empty_data(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'')
        self.assertEqual(b'', stream._buffer)

    def test_feed_nonempty_data(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(self.DATA)
        self.assertEqual(self.DATA, stream._buffer)

    def test_read_zero(self):
        # Read zero bytes.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        data = self.loop.run_until_complete(stream.read(0))
        self.assertEqual(b'', data)
        self.assertEqual(self.DATA, stream._buffer)

    def test_read(self):
        # Read bytes.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = asyncio.Task(stream.read(30), loop=self.loop)

        def cb():
            stream.feed_data(self.DATA)
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(self.DATA, data)
        self.assertEqual(b'', stream._buffer)

    def test_read_line_breaks(self):
        # Read bytes without line breaks.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line1')
        stream.feed_data(b'line2')

        data = self.loop.run_until_complete(stream.read(5))

        self.assertEqual(b'line1', data)
        self.assertEqual(b'line2', stream._buffer)

    def test_read_eof(self):
        # Read bytes, stop at eof.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = asyncio.Task(stream.read(1024), loop=self.loop)

        def cb():
            stream.feed_eof()
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(b'', data)
        self.assertEqual(b'', stream._buffer)

    def test_read_until_eof(self):
        # Read all bytes until eof.
        stream = asyncio.StreamReader(loop=self.loop)
        read_task = asyncio.Task(stream.read(-1), loop=self.loop)

        def cb():
            stream.feed_data(b'chunk1\n')
            stream.feed_data(b'chunk2')
            stream.feed_eof()
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)

        self.assertEqual(b'chunk1\nchunk2', data)
        self.assertEqual(b'', stream._buffer)

    def test_read_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.read(2))
        self.assertEqual(b'li', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.read(2))

    def test_invalid_limit(self):
        with self.assertRaisesRegex(ValueError, 'imit'):
            asyncio.StreamReader(limit=0, loop=self.loop)

        with self.assertRaisesRegex(ValueError, 'imit'):
            asyncio.StreamReader(limit=-1, loop=self.loop)

    def test_read_limit(self):
        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'chunk')
        data = self.loop.run_until_complete(stream.read(5))
        self.assertEqual(b'chunk', data)
        self.assertEqual(b'', stream._buffer)

    def test_readline(self):
        # Read one line. 'readline' will need to wait for the data
        # to come from 'cb'
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'chunk1 ')
        read_task = asyncio.Task(stream.readline(), loop=self.loop)

        def cb():
            stream.feed_data(b'chunk2 ')
            stream.feed_data(b'chunk3 ')
            stream.feed_data(b'\n chunk4')
        self.loop.call_soon(cb)

        line = self.loop.run_until_complete(read_task)
        self.assertEqual(b'chunk1 chunk2 chunk3 \n', line)
        self.assertEqual(b' chunk4', stream._buffer)

    def test_readline_limit_with_existing_data(self):
        # Read one line. The data is in StreamReader's buffer
        # before the event loop is run.

        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'li')
        stream.feed_data(b'ne1\nline2\n')

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # The buffer should contain the remaining data after exception
        self.assertEqual(b'line2\n', stream._buffer)

        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'li')
        stream.feed_data(b'ne1')
        stream.feed_data(b'li')

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # No b'\n' at the end. The 'limit' is set to 3. So before
        # waiting for the new data in buffer, 'readline' will consume
        # the entire buffer, and since the length of the consumed data
        # is more than 3, it will raise a ValueError. The buffer is
        # expected to be empty now.
        self.assertEqual(b'', stream._buffer)

    def test_at_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertFalse(stream.at_eof())

        stream.feed_data(b'some data\n')
        self.assertFalse(stream.at_eof())

        self.loop.run_until_complete(stream.readline())
        self.assertFalse(stream.at_eof())

        stream.feed_data(b'some data\n')
        stream.feed_eof()
        self.loop.run_until_complete(stream.readline())
        self.assertTrue(stream.at_eof())

    def test_readline_limit(self):
        # Read one line. StreamReaders are fed with data after
        # their 'readline' methods are called.

        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        def cb():
            stream.feed_data(b'chunk1')
            stream.feed_data(b'chunk2')
            stream.feed_data(b'chunk3\n')
            stream.feed_eof()
        self.loop.call_soon(cb)

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        # The buffer had just one line of data, and after raising
        # a ValueError it should be empty.
        self.assertEqual(b'', stream._buffer)

        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        def cb():
            stream.feed_data(b'chunk1')
            stream.feed_data(b'chunk2\n')
            stream.feed_data(b'chunk3\n')
            stream.feed_eof()
        self.loop.call_soon(cb)

        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        self.assertEqual(b'chunk3\n', stream._buffer)

        # check strictness of the limit
        stream = asyncio.StreamReader(limit=7, loop=self.loop)
        stream.feed_data(b'1234567\n')
        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'1234567\n', line)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'12345678\n')
        with self.assertRaises(ValueError) as cm:
            self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'12345678')
        with self.assertRaises(ValueError) as cm:
            self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', stream._buffer)

    def test_readline_nolimit_nowait(self):
        # All needed data for the first 'readline' call will be
        # in the buffer.
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA[:6])
        stream.feed_data(self.DATA[6:])

        line = self.loop.run_until_complete(stream.readline())

        self.assertEqual(b'line1\n', line)
        self.assertEqual(b'line2\nline3\n', stream._buffer)

    def test_readline_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'some data')
        stream.feed_eof()

        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'some data', line)

    def test_readline_empty_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_eof()

        line = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'', line)

    def test_readline_read_byte_count(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        self.loop.run_until_complete(stream.readline())

        data = self.loop.run_until_complete(stream.read(7))

        self.assertEqual(b'line2\nl', data)
        self.assertEqual(b'ine3\n', stream._buffer)

    def test_readline_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.readline())
        self.assertEqual(b'line\n', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readline())
        self.assertEqual(b'', stream._buffer)

    def test_readuntil_separator(self):
        stream = asyncio.StreamReader(loop=self.loop)
        with self.assertRaisesRegex(ValueError, 'Separator should be'):
            self.loop.run_until_complete(stream.readuntil(separator=b''))

    def test_readuntil_multi_chunks(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'lineAAA')
        data = self.loop.run_until_complete(stream.readuntil(separator=b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'lineAAA')
        data = self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'lineAAAxxx')
        data = self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(b'lineAAA', data)
        self.assertEqual(b'xxx', stream._buffer)

    def test_readuntil_multi_chunks_1(self):
        stream = asyncio.StreamReader(loop=self.loop)

        stream.feed_data(b'QWEaa')
        stream.feed_data(b'XYaa')
        stream.feed_data(b'a')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'QWEaaXYaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'QWEaa')
        stream.feed_data(b'XYa')
        stream.feed_data(b'aa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'QWEaaXYaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'aaa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'aaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'Xaaa')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'Xaaa', data)
        self.assertEqual(b'', stream._buffer)

        stream.feed_data(b'XXX')
        stream.feed_data(b'a')
        stream.feed_data(b'a')
        stream.feed_data(b'a')
        data = self.loop.run_until_complete(stream.readuntil(b'aaa'))
        self.assertEqual(b'XXXaaa', data)
        self.assertEqual(b'', stream._buffer)

    def test_readuntil_eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'some dataAA')
        stream.feed_eof()

        with self.assertRaises(asyncio.IncompleteReadError) as cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))
        self.assertEqual(cm.exception.partial, b'some dataAA')
        self.assertIsNone(cm.exception.expected)
        self.assertEqual(b'', stream._buffer)

    def test_readuntil_limit_found_sep(self):
        stream = asyncio.StreamReader(loop=self.loop, limit=3)
        stream.feed_data(b'some dataAA')

        with self.assertRaisesRegex(asyncio.LimitOverrunError,
                                    'not found') as cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))

        self.assertEqual(b'some dataAA', stream._buffer)

        stream.feed_data(b'A')
        with self.assertRaisesRegex(asyncio.LimitOverrunError,
                                    'is found') as cm:
            self.loop.run_until_complete(stream.readuntil(b'AAA'))

        self.assertEqual(b'some dataAAA', stream._buffer)

    def test_readexactly_zero_or_less(self):
        # Read exact number of bytes (zero or less).
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(self.DATA)

        data = self.loop.run_until_complete(stream.readexactly(0))
        self.assertEqual(b'', data)
        self.assertEqual(self.DATA, stream._buffer)

        with self.assertRaisesRegex(ValueError, 'less than zero'):
            self.loop.run_until_complete(stream.readexactly(-1))
        self.assertEqual(self.DATA, stream._buffer)

    def test_readexactly(self):
        # Read exact number of bytes.
        stream = asyncio.StreamReader(loop=self.loop)

        n = 2 * len(self.DATA)
        read_task = asyncio.Task(stream.readexactly(n), loop=self.loop)

        def cb():
            stream.feed_data(self.DATA)
            stream.feed_data(self.DATA)
            stream.feed_data(self.DATA)
        self.loop.call_soon(cb)

        data = self.loop.run_until_complete(read_task)
        self.assertEqual(self.DATA + self.DATA, data)
        self.assertEqual(self.DATA, stream._buffer)

    def test_readexactly_limit(self):
        stream = asyncio.StreamReader(limit=3, loop=self.loop)
        stream.feed_data(b'chunk')
        data = self.loop.run_until_complete(stream.readexactly(5))
        self.assertEqual(b'chunk', data)
        self.assertEqual(b'', stream._buffer)

    def test_readexactly_eof(self):
        # Read exact number of bytes (eof).
        stream = asyncio.StreamReader(loop=self.loop)
        n = 2 * len(self.DATA)
        read_task = asyncio.Task(stream.readexactly(n), loop=self.loop)

        def cb():
            stream.feed_data(self.DATA)
            stream.feed_eof()
        self.loop.call_soon(cb)

        with self.assertRaises(asyncio.IncompleteReadError) as cm:
            self.loop.run_until_complete(read_task)
        self.assertEqual(cm.exception.partial, self.DATA)
        self.assertEqual(cm.exception.expected, n)
        self.assertEqual(str(cm.exception),
                         '18 bytes read on a total of 36 expected bytes')
        self.assertEqual(b'', stream._buffer)

    def test_readexactly_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'line\n')

        data = self.loop.run_until_complete(stream.readexactly(2))
        self.assertEqual(b'li', data)

        stream.set_exception(ValueError())
        self.assertRaises(
            ValueError, self.loop.run_until_complete, stream.readexactly(2))

    def test_exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertIsNone(stream.exception())

        exc = ValueError()
        stream.set_exception(exc)
        self.assertIs(stream.exception(), exc)

    def test_exception_waiter(self):
        stream = asyncio.StreamReader(loop=self.loop)

        @asyncio.coroutine
        def set_err():
            stream.set_exception(ValueError())

        t1 = asyncio.Task(stream.readline(), loop=self.loop)
        t2 = asyncio.Task(set_err(), loop=self.loop)

        self.loop.run_until_complete(asyncio.wait([t1, t2], loop=self.loop))

        self.assertRaises(ValueError, t1.result)

    def test_exception_cancel(self):
        stream = asyncio.StreamReader(loop=self.loop)

        t = asyncio.Task(stream.readline(), loop=self.loop)
        test_utils.run_briefly(self.loop)
        t.cancel()
        test_utils.run_briefly(self.loop)
        # The following line fails if set_exception() isn't careful.
        stream.set_exception(RuntimeError('message'))
        test_utils.run_briefly(self.loop)
        self.assertIs(stream._waiter, None)

    def test_start_server(self):

        class MyServer:

            def __init__(self, loop):
                self.server = None
                self.loop = loop

            @asyncio.coroutine
            def handle_client(self, client_reader, client_writer):
                data = yield from client_reader.readline()
                client_writer.write(data)
                yield from client_writer.drain()
                client_writer.close()

            def start(self):
                sock = socket.socket()
                sock.bind(('127.0.0.1', 0))
                self.server = self.loop.run_until_complete(
                    asyncio.start_server(self.handle_client,
                                         sock=sock,
                                         loop=self.loop))
                return sock.getsockname()

            def handle_client_callback(self, client_reader, client_writer):
                self.loop.create_task(self.handle_client(client_reader,
                                                         client_writer))

            def start_callback(self):
                sock = socket.socket()
                sock.bind(('127.0.0.1', 0))
                addr = sock.getsockname()
                sock.close()
                self.server = self.loop.run_until_complete(
                    asyncio.start_server(self.handle_client_callback,
                                         host=addr[0], port=addr[1],
                                         loop=self.loop))
                return addr

            def stop(self):
                if self.server is not None:
                    self.server.close()
                    self.loop.run_until_complete(self.server.wait_closed())
                    self.server = None

        @asyncio.coroutine
        def client(addr):
            reader, writer = yield from asyncio.open_connection(
                *addr, loop=self.loop)
            # send a line
            writer.write(b"hello world!\n")
            # read it back
            msgback = yield from reader.readline()
            writer.close()
            return msgback

        # test the server variant with a coroutine as client handler
        server = MyServer(self.loop)
        addr = server.start()
        msg = self.loop.run_until_complete(asyncio.Task(client(addr),
                                                        loop=self.loop))
        server.stop()
        self.assertEqual(msg, b"hello world!\n")

        # test the server variant with a callback as client handler
        server = MyServer(self.loop)
        addr = server.start_callback()
        msg = self.loop.run_until_complete(asyncio.Task(client(addr),
                                                        loop=self.loop))
        server.stop()
        self.assertEqual(msg, b"hello world!\n")

    @unittest.skipUnless(hasattr(socket, 'AF_UNIX'), 'No UNIX Sockets')
    def test_start_unix_server(self):

        class MyServer:

            def __init__(self, loop, path):
                self.server = None
                self.loop = loop
                self.path = path

            @asyncio.coroutine
            def handle_client(self, client_reader, client_writer):
                data = yield from client_reader.readline()
                client_writer.write(data)
                yield from client_writer.drain()
                client_writer.close()

            def start(self):
                self.server = self.loop.run_until_complete(
                    asyncio.start_unix_server(self.handle_client,
                                              path=self.path,
                                              loop=self.loop))

            def handle_client_callback(self, client_reader, client_writer):
                self.loop.create_task(self.handle_client(client_reader,
                                                         client_writer))

            def start_callback(self):
                start = asyncio.start_unix_server(self.handle_client_callback,
                                                  path=self.path,
                                                  loop=self.loop)
                self.server = self.loop.run_until_complete(start)

            def stop(self):
                if self.server is not None:
                    self.server.close()
                    self.loop.run_until_complete(self.server.wait_closed())
                    self.server = None

        @asyncio.coroutine
        def client(path):
            reader, writer = yield from asyncio.open_unix_connection(
                path, loop=self.loop)
            # send a line
            writer.write(b"hello world!\n")
            # read it back
            msgback = yield from reader.readline()
            writer.close()
            return msgback

        # test the server variant with a coroutine as client handler
        with test_utils.unix_socket_path() as path:
            server = MyServer(self.loop, path)
            server.start()
            msg = self.loop.run_until_complete(asyncio.Task(client(path),
                                                            loop=self.loop))
            server.stop()
            self.assertEqual(msg, b"hello world!\n")

        # test the server variant with a callback as client handler
        with test_utils.unix_socket_path() as path:
            server = MyServer(self.loop, path)
            server.start_callback()
            msg = self.loop.run_until_complete(asyncio.Task(client(path),
                                                            loop=self.loop))
            server.stop()
            self.assertEqual(msg, b"hello world!\n")

    @unittest.skipIf(sys.platform == 'win32', "Don't have pipes")
    def test_read_all_from_pipe_reader(self):
        # See asyncio issue 168.  This test is derived from the example
        # subprocess_attach_read_pipe.py, but we configure the
        # StreamReader's limit so that twice it is less than the size
        # of the data writter.  Also we must explicitly attach a child
        # watcher to the event loop.

        code = """\
import os, sys
fd = int(sys.argv[1])
os.write(fd, b'data')
os.close(fd)
"""
        rfd, wfd = os.pipe()
        args = [sys.executable, '-c', code, str(wfd)]

        pipe = open(rfd, 'rb', 0)
        reader = asyncio.StreamReader(loop=self.loop, limit=1)
        protocol = asyncio.StreamReaderProtocol(reader, loop=self.loop)
        transport, _ = self.loop.run_until_complete(
            self.loop.connect_read_pipe(lambda: protocol, pipe))

        watcher = asyncio.SafeChildWatcher()
        watcher.attach_loop(self.loop)
        try:
            asyncio.set_child_watcher(watcher)
            create = asyncio.create_subprocess_exec(*args,
                                                    pass_fds={wfd},
                                                    loop=self.loop)
            proc = self.loop.run_until_complete(create)
            self.loop.run_until_complete(proc.wait())
        finally:
            asyncio.set_child_watcher(None)

        os.close(wfd)
        data = self.loop.run_until_complete(reader.read(-1))
        self.assertEqual(data, b'data')

    def test_streamreader_constructor(self):
        self.addCleanup(asyncio.set_event_loop, None)
        asyncio.set_event_loop(self.loop)

        # asyncio issue #184: Ensure that StreamReaderProtocol constructor
        # retrieves the current loop if the loop parameter is not set
        reader = asyncio.StreamReader()
        self.assertIs(reader._loop, self.loop)

    def test_streamreaderprotocol_constructor(self):
        self.addCleanup(asyncio.set_event_loop, None)
        asyncio.set_event_loop(self.loop)

        # asyncio issue #184: Ensure that StreamReaderProtocol constructor
        # retrieves the current loop if the loop parameter is not set
        reader = mock.Mock()
        protocol = asyncio.StreamReaderProtocol(reader)
        self.assertIs(protocol._loop, self.loop)

    def test_drain_raises(self):
        # See http://bugs.python.org/issue25441

        # This test should not use asyncio for the mock server; the
        # whole point of the test is to test for a bug in drain()
        # where it never gives up the event loop but the socket is
        # closed on the  server side.

        q = queue.Queue()

        def server():
            # Runs in a separate thread.
            sock = socket.socket()
            with sock:
                sock.bind(('localhost', 0))
                sock.listen(1)
                addr = sock.getsockname()
                q.put(addr)
                clt, _ = sock.accept()
                clt.close()

        @asyncio.coroutine
        def client(host, port):
            reader, writer = yield from asyncio.open_connection(
                host, port, loop=self.loop)

            while True:
                writer.write(b"foo\n")
                yield from writer.drain()

        # Start the server thread and wait for it to be listening.
        thread = threading.Thread(target=server)
        thread.setDaemon(True)
        thread.start()
        addr = q.get()

        # Should not be stuck in an infinite loop.
        with self.assertRaises((ConnectionResetError, BrokenPipeError)):
            self.loop.run_until_complete(client(*addr))

        # Clean up the thread.  (Only on success; on failure, it may
        # be stuck in accept().)
        thread.join()

    def test___repr__(self):
        stream = asyncio.StreamReader(loop=self.loop)
        self.assertEqual("<StreamReader>", repr(stream))

    def test___repr__nondefault_limit(self):
        stream = asyncio.StreamReader(loop=self.loop, limit=123)
        self.assertEqual("<StreamReader l=123>", repr(stream))

    def test___repr__eof(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_eof()
        self.assertEqual("<StreamReader eof>", repr(stream))

    def test___repr__data(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream.feed_data(b'data')
        self.assertEqual("<StreamReader 4 bytes>", repr(stream))

    def test___repr__exception(self):
        stream = asyncio.StreamReader(loop=self.loop)
        exc = RuntimeError()
        stream.set_exception(exc)
        self.assertEqual("<StreamReader e=RuntimeError()>", repr(stream))

    def test___repr__waiter(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream._waiter = asyncio.Future(loop=self.loop)
        self.assertRegex(
            repr(stream),
            "<StreamReader w=<Future pending[\S ]*>>")
        stream._waiter.set_result(None)
        self.loop.run_until_complete(stream._waiter)
        stream._waiter = None
        self.assertEqual("<StreamReader>", repr(stream))

    def test___repr__transport(self):
        stream = asyncio.StreamReader(loop=self.loop)
        stream._transport = mock.Mock()
        stream._transport.__repr__ = mock.Mock()
        stream._transport.__repr__.return_value = "<Transport>"
        self.assertEqual("<StreamReader t=<Transport>>", repr(stream))


if __name__ == '__main__':
    unittest.main()
