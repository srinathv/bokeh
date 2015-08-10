from __future__ import absolute_import, print_function
import os
import pytest

from bokeh.io import output_file
from .webserver import SimpleWebServer


@pytest.fixture(scope='session', autouse=True)
def server(request):
    server = SimpleWebServer()
    server.start()

    def stop_server():
        server.stop()
    request.addfinalizer(stop_server)

    return server


@pytest.fixture
def output_file_url(request, server):

    filename = request.function.__name__ + '.html'
    file_path = request.fspath.dirpath().join(filename).strpath

    output_file(file_path)

    def fin():
        os.remove(file_path)
    request.addfinalizer(fin)

    return 'http://%s:%s/%s' % (server.host, server.port, file_path)
