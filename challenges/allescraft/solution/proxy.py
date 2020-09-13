import socket
import threading
import logging
import select
import time


class Proxy(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.running = False
        self.cb = lambda data: 0
        self.last_con = None
        self.packets = 0
        self.lt = time.time()

    def bind(self, addr):
        self.sock.bind(addr)

    def run(self):
        self.running = True
        self.sock.listen(5)
        while self.running:
            ready = select.select([self.sock], [], [], 2)
            if ready[0]:
                conn, addr = self.sock.accept()
                self.last_con = conn
                print(f"Connection {addr}")
                with conn:
                    while self.running:
                        ready = select.select([conn], [], [conn], 2)
                        if ready[0]:
                            try:
                                data = conn.recv(4096)
                            except:
                                break
                            if not data:
                                break
                            self.cb(data)
                        if ready[2]:
                            break
                self.last_con = None
        self.sock.close()

    def send(self, msg):
        self.packets += 1
        if time.time() - self.lt > 1:
            self.lt = time.time()
            print(f"pps: {self.packets}")
            self.packets = 0
        if not self.running or not msg or not self.last_con:
            return
        self.last_con.send(msg)


class Interceptor:
    def __init__(self):
        pass

    def intercept(self, data, from_server):
        return data


class DoubleProxy:

    def __init__(self, listen_addr, listen_srv_addr, interceptor=Interceptor()):
        self.to_client = Proxy()
        self.to_server = Proxy()
        self.to_client.bind(listen_addr)
        self.to_server.bind(listen_srv_addr)
        self.to_client.cb = lambda data: self.to_server.send(
            interceptor.intercept(data, False))
        self.to_server.cb = lambda data: self.to_client.send(
            interceptor.intercept(data, True))

    def start(self):
        logging.info("starting double proxy")
        self.to_client.start()
        logging.info("client proxy running..")
        self.to_server.start()
        logging.info("server proxy running..")

    def stop(self):
        logging.info("stopping double proxy")
        self.to_client.running = False
        self.to_server.running = False
        self.to_client.join()
        logging.info("client proxy stopped..")
        self.to_server.join()
        logging.info("server proxy stopped..")


def main():
    dp = DoubleProxy(('0.0.0.0', 4337), ("0.0.0.0", 2337))
    dp.start()
    while True:
        pass
    dp.stop()


if __name__ == "__main__":
    main()
