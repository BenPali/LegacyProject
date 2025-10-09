class Request:
    def __init__(self, method, path, headers, body):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


class Response:
    def __init__(self, status=200, headers=None, body=''):
        self.status = status
        self.headers = headers or {}
        self.body = body


class Server:
    def __init__(self, port=8080):
        self.port = port
        self.handlers = []
    
    def add_handler(self, handler):
        self.handlers.append(handler)
    
    def start(self):
        pass
    
    def stop(self):
        pass
