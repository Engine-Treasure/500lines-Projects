# -*- coding: utf-8 -*-



import socket

q = []


def parse_links(response):
    pass


def fetch(url):
    from selectors import DefaultSelector, EVENT_WRITE

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
    q.add(links)
