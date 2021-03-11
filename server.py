import socket
import threading
import logging
import sys




class MyServer(socket.socket):
    HOST = '127.0.0.1'

    def __init__(self, port):
        self._log()
        self.port = port
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((self.HOST, self.port))
        self.create_flags()

    def create_flags(self):
        names = [
            'start_talking',
            'end_talking',
            'a',
            'b',
        ]
        for nm in names:
            setattr(self, nm, threading.Event())

    def send_message(self,msg):
        self.conn.sendall(msg.encode('utf8'))
        self.log.info(f'sent message - {msg}')

    def duties(self):
        if self.end_talking.is_set():
            return True

        if self.a.is_set():
            self.a.clear()
            self.send_message('I have nothing to say')

        if self.b.is_set():
            self.b.clear()
            self.send_message('We are done')

        return False

    def process_message(self, msg):
        if msg == 'done':
            self.end_talking.set()
        elif msg == 'first':
            self.a.set()
        elif msg == 'second':
            self.b.set()
    
    def talk(self):
        self.start_talking.wait()
        self.log.info('connection made - can talk now')
        while True:
            if self.duties():
                break
        self.log.info('talk thread ending')


    def hear(self):
        self.listen()
        self.conn, self.addr = self.accept()
        self.log.info(f'connection with - {self.addr}')
        self.start_talking.set()
        while True:
            data = self.conn.recv(1024)
            if not data:
                self.log.info('no data received')
                break 
            else:
                self.process_message(data.decode('utf8'))

        self.log.info('listening thread ending')
        self.end_talking.set()
        self.close()

    def run(self):
        self.log.info("starting talk and listen threads")

        threads = [
            threading.Thread(target=self.talk),
            threading.Thread(target=self.hear),
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def _log(self):
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
        )
        self.log = logging.getLogger(__name__)


#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#   s.bind((HOST,PORT))
#   s.listen()
#   conn, addr = s.accept()
#   with conn:
#       print('connection by ', addr)
#       while True:
#           data = conn.recv(1024)
#           if not data:
#               break
#           conn.sendall(data)




if __name__ == '__main__':
    server = MyServer(12345)
    server.run()
