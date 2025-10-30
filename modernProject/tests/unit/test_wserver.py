import pytest
from lib.wserver import Request, Response, Server


def test_request_creation():
    req = Request("GET", "/index.html", {"Host": "localhost"}, "")
    assert req.method == "GET"
    assert req.path == "/index.html"
    assert req.headers == {"Host": "localhost"}
    assert req.body == ""


def test_request_with_body():
    body = '{"key": "value"}'
    req = Request("POST", "/api/data", {"Content-Type": "application/json"}, body)
    assert req.method == "POST"
    assert req.path == "/api/data"
    assert req.body == body


def test_response_default():
    resp = Response()
    assert resp.status == 200
    assert resp.headers == {}
    assert resp.body == ''


def test_response_custom():
    resp = Response(status=404, headers={"Content-Type": "text/html"}, body="Not Found")
    assert resp.status == 404
    assert resp.headers == {"Content-Type": "text/html"}
    assert resp.body == "Not Found"


def test_response_with_headers():
    headers = {"Content-Type": "application/json", "Cache-Control": "no-cache"}
    resp = Response(status=201, headers=headers, body='{"created": true}')
    assert resp.status == 201
    assert resp.headers == headers
    assert resp.body == '{"created": true}'


def test_server_creation():
    server = Server()
    assert server.port == 8080
    assert server.handlers == []


def test_server_custom_port():
    server = Server(port=3000)
    assert server.port == 3000


def test_server_add_handler():
    server = Server()

    def handler(req):
        return Response(body="handled")

    server.add_handler(handler)
    assert len(server.handlers) == 1
    assert server.handlers[0] == handler


def test_server_add_multiple_handlers():
    server = Server()

    def handler1(req):
        return Response(body="handler1")

    def handler2(req):
        return Response(body="handler2")

    server.add_handler(handler1)
    server.add_handler(handler2)
    assert len(server.handlers) == 2


def test_server_start():
    server = Server()
    server.start()


def test_server_stop():
    server = Server()
    server.stop()


def test_server_lifecycle():
    server = Server(port=9000)
    server.start()
    server.stop()
