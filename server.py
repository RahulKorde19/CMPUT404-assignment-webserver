#  coding: utf-8 
import socketserver
import os
import mimetypes

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


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        data_decoded = self.data.decode('utf-8')

        # Parse the request
        request_line = data_decoded.split('\r\n')[0]
        request_method, request_path, _ = request_line.split()

        # Check for accessing sensitive system files
        if "../" in request_path:
            self.HTTP_message(404, "Not Found")
            return

        # Check for GET method
        if request_method != "GET":
            self.HTTP_message(405, "Method Not Allowed")
            return

        # Get the file path
        current_dir = os.getcwd()
        path = os.path.join(current_dir, "www", request_path.strip('/'))

        # Handle directory redirection
        if os.path.isdir(path):
            if not request_path.endswith("/"):
                self.HTTP_message(301, "Moved Permanently", location=request_path + '/')
                return
            path = os.path.join(path, "index.html")

        # Check if the file or directory exists
        if not os.path.exists(path):
            self.HTTP_message(404, "Not Found")
            return
            

        # Get content type and content length
        content_length = os.path.getsize(path)
        mime_type, _ = mimetypes.guess_type(path)

        # Read the content of the file
        with open(path, 'rb') as f:
            content = f.read()

        # Send the response
        self.HTTP_message(200, "OK", content_type=mime_type, content=content)

    def HTTP_message(self, HTTP_status_code, HTTP_status_message, location=None, content_type=None, content=None):
        HTTP_headers_response = f"HTTP/1.1 {HTTP_status_code} {HTTP_status_message}\r\n"

        if location:
            HTTP_headers_response += f"Location: {location}\r\n"

        if content_type:
            HTTP_headers_response += f"Content-Type: {content_type}\r\n"

        if content:
            HTTP_headers_response += f"Content-Length: {len(content)}\r\n\r\n"
            binary_response = HTTP_headers_response.encode('utf-8') + content

        else:
            HTTP_headers_response += "\r\n"
            binary_response = HTTP_headers_response.encode('utf-8')

        self.request.sendall(binary_response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
