import http.server
import queue, json


class RequestHandlerImpl(http.server.BaseHTTPRequestHandler):
    """
    自定义一个 HTTP 请求处理器
    """

    def do_GET(self):
        """
        处理 GET 请求, 处理其他请求需实现对应的 do_XXX() 方法
        """
        # print(self.server)                # HTTPServer 实例
        # print(self.client_address)        # 客户端地址和端口: (host, port)
        # print(self.requestline)           # 请求行, 例如: 'GET / HTTP/1.1'
        # print(self.command)               # 请求方法, 'GET'/'POST'等
        # print(self.path)                  # 请求路径, Host 后面部分
        # print(self.headers)               # 请求头, 通过 headers['header_name'] 获取值
        # self.rfile                        # 请求输入流
        # self.wfile                        # 响应输出流

        # 1. 发送响应code
        self.send_response(200)

        # 2. 发送响应头
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        # 3. 发送响应内容（此处流不需要关闭）
        self.wfile.write("Hello World\n".encode("utf-8"))

    def do_POST(self):
        """
        处理 POST 请求
        """
        # 0. 获取请求Body中的内容（需要指定读取长度, 不指定会阻塞）
        req_body = self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8")
        # print('req_body: {}'.format(req_body))
        # print('req_body-type: {}'.format(self.headers['Content-Type']))
        # print('chat_id: {}\nmagnet_url: {}'.format(json.loads(req_body)['chat_id'], json.loads(req_body)['magnet_url']))
        data_queue.put(
            {
                "chat_id": json.loads(req_body)["chat_id"],
                "magnet_url": json.loads(req_body)["magnet_url"],
            }
        )

        # 1. 发送响应code
        self.send_response(200)

        # 2. 发送响应头
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        # 3. 发送响应内容（此处流不需要关闭）
        self.wfile.write(("Hello World: " + req_body + "\n").encode("utf-8"))


def simple_http_server(task_queue):
    global data_queue
    data_queue = task_queue
    # 服务器绑定的地址和端口
    server_address = ("", 8000)

    # 创建一个 HTTP 服务器（Web服务器）, 指定绑定的地址/端口 和 请求处理器
    httpd = http.server.HTTPServer(server_address, RequestHandlerImpl)

    # 循环等待客户端请求
    httpd.serve_forever()
