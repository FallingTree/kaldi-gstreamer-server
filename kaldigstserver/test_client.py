# -*- encoding: UTF-8 -*-
from ws4py.client.threadedclient import WebSocketClient
import threading
import time
import sys
import os
import Queue
import json

class MyClient(WebSocketClient):

    def __init__(self, filename, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.fn = filename
        self.byterate = byterate
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

    def opened(self):
        print "Socket opened!"
        def send_data_to_ws():
            f = open(self.fn, "rb")
            for block in iter(lambda: f.read(self.byterate/4), ""):
                self.send(block)
            print >> sys.stderr, "Audio sent, now sending EOS"
            f.close()
            self.send("EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        print "Received message"
        

if __name__ == '__main__':
    try:
        uri = "ws://localhost:8888/client/ws/speech"
        ws = MyClient("test/data/english_test.wav", uri, byterate=4800)

        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
