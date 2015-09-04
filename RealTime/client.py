# -*- encoding: UTF-8 -*-

from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib
import Queue
import json
from Tkinter import *
from utterance import Utterance


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

    def __init__(self,TextArea,latence, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.byterate = byterate
        self.isSending = True
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename

        self.TextArea = TextArea
        self.latence = latence

        self.start_currTrans = "1.0"
        self.trans = []
        self.premiere_hypothese = True
        utt = Utterance()
        self.currUtterance = utt
        self.nextUtterance = utt
        self.newUtt = threading.Event()

        self.decoder_available = True

    #@rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        print "* Socket opened!"
        def send_data_to_ws():

            # If we want to send adaptation state
            if self.send_adaptation_state_filename is not None:
                print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print >> sys.stderr, "Failed to send adaptation state: ",  e

            # Managing the life of the Utterance
            while self.isSending:
                if self.currUtterance is not self.nextUtterance:
                    self.currUtterance = self.nextUtterance
                    self.currUtterance.event_started.wait()
                    self.currUtterance.wait_end_utt_recording()
                    self.currUtterance.wait_final_result(0.5)
                    self.premiere_hypothese = True
                    self.currUtterance.set_end_utt()
                    self.newUtt.wait()


            print "* Audio finished : sending EOS"    
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
                    print_trans = trans.replace("\n", "\\n")
                    #print >> sys.stderr, '\r%s' % print_trans
                    print "Hypothese finale : ", print_trans
                    print "** Time received final result : ", time.strftime("%A %d %B %Y %H:%M:%S")

                    # Deleting the partial transcription and replacing by the final hypothesis
                    self.TextArea.delete(self.start_currTrans,"end")
                    self.TextArea.insert('end',print_trans)
                    self.TextArea.see(END)
                    self.start_currTrans = self.TextArea.index(INSERT)

                    self.trans = []
                    self.currUtterance.set_final_result()

                    if self.isSending:
                        # If the recording of the utterance has ended raise the event to move on the next utterance
                        if self.currUtterance.event_end_recording.isSet():
                            print "Setting Final Result event"
                            self.currUtterance.set_final_result()
                            self.currUtterance.set_got_final_result()
                            self.newUtt.wait()
                        
                                          
                else:

                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    # print >> sys.stderr, '\r%s' % print_trans,
                    print "Hypothese intermediaire : ", print_trans
                    
                    # If 1st hypothesis of the utterance, we store the time and compute the time it took to transcribe
                    if self.premiere_hypothese:
                        self.currUtterance.set_first_result()
                        latency =  self.currUtterance.get_latence()
                        self.latence["text"] = "Subs Latence : %.2f s" % latency
                        self.premiere_hypothese = False


                    # Deleting the part of the result that was already previouly written in the TextArea
                    transcription = str(print_trans.encode('utf-8'))
                    self.TextArea.delete(self.start_currTrans,"end")
                    self.TextArea.insert('end',transcription)
                    self.TextArea.see(END)


                    # Saving the transcript in the Utterance
                    self.currUtterance.set_transcript(transcription)


                


            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print >> sys.stderr, "Received error from server (status %d)" % response['status']
            if 'message' in response:
                print >> sys.stderr, "Error message:",  response['message']
            if response['message']=="No decoder available, try again later":
                self.decoder_available = False



    def get_full_hyp(self, timeout=3600):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        print "Websocket closed() called"
        #print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))

    def start_Sending(self):
        self.isSending = True

    def stop_Sending(self):
        self.isSending = False

    def set_utterance(self,utterance):
        self.nextUtterance = utterance
        self.newUtt.set()



