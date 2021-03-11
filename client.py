import socket
import threading
import logging
import sys




class MyClient(socket.socket):

    def __init__(self, host, port):
        self._log()
        self.HOST = host
        self.PORT = port
        self.create_flags()
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)

    def create_flags(self):
        names = [
            'start_talking',
            'end_talking',
            'a',
        ]
        for nm in names:
            setattr(self, nm, threading.Event())

    def send_message(self,msg):
        self.sendall(msg.encode('utf8'))
        self.log.info(f'sent message - {msg}')

    def duties(self):
        if not self.start_talking.is_set():
            self.start_talking.set()
            self.send_message('first')
        
        if self.a.is_set():
            self.a.clear()
            self.send_message('second')

        return False

    def talk(self):
        self.connect((self.HOST,self.PORT))
        self.log.info('connection made - can talk now')

        while True:
            self.duties()
            if self.end_talking.is_set():
                break

        self.log.info('talk thread ending')

    def process_message(self, msg):
        if msg == "I have nothing to say":
            self.a.set()

        if msg == "We are done":
            self.end_talking.set()
            return True

        False

    def hear(self):
        while True:
            data = self.recv(1024)
            if self.process_message(data.decode('utf8')):
                break

        self.log.info('listening thread ending')
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




if __name__ == '__main__':
    client = MyClient('127.0.0.1', 12345)
    client.run()
