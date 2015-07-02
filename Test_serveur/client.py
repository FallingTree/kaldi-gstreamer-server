# -*- encoding: UTF-8 -*-

import argparse
from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib
import Queue
import json
import time
import os
from gi.repository import GObject
from recorder import *

def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class MyClient(WebSocketClient):

    def __init__(self, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.frames = None
        self.byterate = byterate
        self.isSending = True
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.currSegment = -1
        self.encours = False
        self.segment_sending = 0 

    @rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        #print "Socket opened!"
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print >> sys.stderr, "Failed to send adaptation state: ",  e

            
            while self.isSending:
                if self.currSegment == self.segment_sending and self.currSegment != -1 :
                    self.encours = True
                    print "Sengment envoyé : ", self.currSegment
                    # print "Longeur chunk : ", len(b''.join(self.frames[1]))
                    # for k in range(0,len(self.frames)):
                    #     #print "k = ", k
                    #     #print self.frames[0]
                    #     self.send_data(b''.join(self.frames[k]))
                    self.send_data(b''.join(self.frames))
                    self.segment_sending+=1
                    self.encours = False
            print >> sys.stderr, "Audio sent, now sending EOS"
            self.send("EOS")


        t = threading.Thread(target=send_data_to_ws)
        t.start()


    def received_message(self, m):
        response = json.loads(str(m))
        #print >> sys.stderr, "RESPONSE:", response
        #print >> sys.stderr, "JSON was:", m
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    #print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    print >> sys.stderr, '\r%s' % trans.replace("\n", "\\n")
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    print >> sys.stderr, '\r%s' % print_trans,
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print >> sys.stderr, "Received error from server (status %d)" % response['status']
            if 'message' in response:
                print >> sys.stderr, "Error message:",  response['message']


    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        print "Websocket closed() called"
        #print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))

    def start_Sending(self):
        self.isSending = True

    def stop_Sending(self):
        self.isSending = False

    def send_frames(self,frames):
        if self.currSegment > -1 :
            while self.encours or self.segment_sending - (self.currSegment +1) > 1:
                time.sleep(0.1)
        self.frames = list(frames)
        self.currSegment += 1



def main():

    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri", help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int, help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='', help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    args = parser.parse_args()

    content_type = args.content_type
   

    try :   
        # Lancer la classe qui gère l'enregistrement
        recorder = Recorder(args.rate)
        recorder.start()

        print "* Recording "
        recorder.start_recording()

        longueur_segment = int(recorder.rate / recorder.chunk * 5)
        start_currSegment = 0
        frames = []
        k=0

        print "Connecting to the Socket"
        # Lancer la classe qui gère l'envoi de données au serveur
        ws = MyClient(args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])), byterate=args.rate,
                          save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)

        
        ws.connect()
        #ws.run_forever()

        
        while True:
            # On verifie que que le buffer a eu assez de donnees pour pouvoir copier
            if len(recorder.buffer) > start_currSegment+longueur_segment+1:
                # On copie la partie du buffer qui nous interesse
                for i in range(0, longueur_segment):
                    frames.append(recorder.buffer[start_currSegment+i])
                ws.send_frames(frames)

                start_currSegment+=longueur_segment
                frames = []


        ws.stop_Sending()


        result = ws.get_full_hyp()
        print result.encode('utf-8')

    except KeyboardInterrupt:
        print "Interrupted by user, Shutting Down"
        recorder.stop()
        ws.stop_Sending()
        ws.close()
        sys.exit(0)



if __name__ == "__main__":
    main()

