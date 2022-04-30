# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from json import dumps

hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        list_path = self.path.split("/")
        print(list_path)
        if list_path[1] == "send":
            print("/send")
            self.wfile.write(bytes(dumps({"message": ''.join(list_path[2::])}), "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")