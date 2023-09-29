#  coding: utf-8 
import socketserver
from typing import Optional
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


def parseHttpRequest(request: str) -> Optional[dict]:
    try:
        parsed_value = {}
        tokens = request.split()
        parsed_value['method'] = tokens[0]
        parsed_value['pathname'] = tokens[1]
        tokens = request.split("\r\n")
        
        return parsed_value
    except:
        return None;

def createHtmlResponse(content: str) -> bytes:
    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r' + content + '\r\n'
    return response.encode()

def createCssResponse(content: str) -> bytes:
    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/css; charset=UTF-8\r\n\r' + content + '\r\n'
    return response.encode()

def createPlainTextResponse(content: str) -> bytes:
    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=UTF-8\r\n\r' + content + '\r\n'
    return response.encode()


def create301Response(location: str) -> bytes:
    response = 'HTTP/1.1 301 Moved Permanently\r\nLocation: ' + location +'\r\n'
    return response.encode()

def create404Response() -> bytes:
    html_404_content = ''
    try:
        with open('./404.html', 'r') as file:
            html_404_content = file.read()
    except:
        pass
    response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + html_404_content + '\r\n'
    return response.encode()

def create405Response() -> bytes:
    html_405_content = ''
    try:
        with open('./405.html', 'r') as file:
            html_405_content = file.read()
    except:
        pass
    response = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + html_405_content + '\r\n'
    return response.encode()


def isValidPath(path: str) -> bool:
    abs_path = os.path.abspath(path)
    accessiable_path = os.path.abspath('./www')
    if abs_path.startswith(accessiable_path):
        return True
    return False

def handle_GET(pathname) -> bytes:
    try:
        file_path = ""
        file_type = ""
        if pathname.endswith('/'):
            file_path = './www' + pathname + 'index.html'
        elif pathname == '/deep':
            response = create301Response('http://127.0.0.1:8080/deep/')
            return response
        else:
            file_path = './www' + pathname
        
        if file_path.endswith(".html"):
            file_type = "html"
        elif file_path.endswith(".css"):
            file_type = "css"
        
        if not isValidPath(file_path):
            response = create404Response()
            return response

        with open(file_path, 'r') as file:
            file_content = file.read()
            response = ''
            if file_type == 'html':
                response = createHtmlResponse(file_content)
            elif file_type == 'css':
                response = createCssResponse(file_content)
            else:
                response = createPlainTextResponse(file_content)
            
            return response
    except FileNotFoundError:
        response = create404Response()
        return response
                



class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        unsupported_methods = set(['POST', 'PUT', 'HEAD', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
        self.data = self.request.recv(1024).strip()
        string_data = self.data.decode('utf-8')
        parsed_request = parseHttpRequest(string_data)
        http_method = parsed_request['method']
        pathname = parsed_request['pathname']

        print("Received:", string_data)

        if http_method == 'GET':
            response = handle_GET(pathname)
            self.request.sendall(response)
            print("Respond:", response.decode('utf-8'))
        elif http_method in unsupported_methods:
            response = create405Response()
            self.request.sendall(response)
            print("Respond:", response.decode('utf-8'))

        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
