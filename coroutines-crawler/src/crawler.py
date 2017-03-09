# -*- coding: utf-8 -*-


import socket

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

urls_todo = set(["/"])
seen_urls = set(["/"])

stopped = False


def parse_links(response):
    pass


def fetch(url):
    selector = DefaultSelector()  # Choose best select-like function on system

    sock = socket.socket()
    sock.setblocking(False)  # by default, socket ops are blocking
    try:  # a non-blocking socket throws an exception from connect, even when it is working normally
        sock.connect(("xkcd.com", 80))
    except BlockingIOError:
        pass

    def connected():
        selector.unregister(sock.fileno())
        print("Connected.")

    # 注册等待事件
    # EVENT_WRITE 表示 socket 可写的触发时间
    # connected 是回调函数. 查看 register 的参数可知, 它被存储为了 data, 更具体点是 event_key.data
    selector.register(sock.fileno(), EVENT_WRITE, connected)

    def loop():
        while True:
            events = selector.select()  # call to select here pauses? 异步等待下一个 IO 事件
            for event_key, event_mask in events:
                callback = event_key.data  # 执行等待事件发生的回调函数
                callback()  # 未完成的操作等到未来的事件循环的某个时钟来到再执行

    request = "GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n".format(url)
    encoded = request.encode("ascii")

    while True:
        try:
            sock.send(encoded)
        except OSError as e:
            pass
    print("Sent")

    response = b''
    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)

    links = parse_links(response)
    seen_urls.add(links)


class Fetcher:
    def __init__(self, url):
        self.response = b''
        self.url = url
        self.sock = None

    def fetch(self):
        '''
        The method returns before the connection is established.
        It must return control to the event loop to wait for the connection.
        :return:
        '''
        sock = socket.socket()
        sock.setblocking(False)  # by default, socket ops are blocking

        try:  # a non-blocking socket throws an exception from connect, even when it is working normally
            sock.connect(("xkcd.com", 80))
        except BlockingIOError:
            pass

        # Register next callback
        selector.register(self.sock.fileno(),
                          EVENT_WRITE,
                          self.connected)

    def connected(self, key, mask):
        print("Connected~")
        selector.unregister(key.fd)
        request = "GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n".format(self.url)
        self.sock.send(request.encode("ascii"))

        selector.register(key.fd,
                          EVENT_READ,
                          self.read_response)


    def read_response(self, key, mask):
        global stopped

        # 此处没有循环. 如果数据没有读完, socket 将保持可读状态,
        # 事件循环的下一个时钟到来时, 继续读取
        # 数据读取完毕, 服务器会关闭 socket, 读出的 chunk 将为空
        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)  # Done reading.
            links = self.parse_links()

            for link in links.difference(seen_urls):
                urls_todo.add(link)
                Fetcher(link).fetch()  # New Fetcher

            seen_urls.update(links)
            urls_todo.remove(self.url)
            if not urls_todo:
                stopped = True


if __name__ == '__main__':
    fetcher = Fetcher("/353/")
    fetcher.fetch()

    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_maskj)
