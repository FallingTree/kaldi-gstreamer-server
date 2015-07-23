# -*- encoding: UTF-8 -*-
import time
import threading
import wave
import audioop
from utterance import Utterance

class Sender(threading.Thread): 
    def __init__(self,ws,recorder,args,textbox):
    	threading.Thread.__init__(self) 
    	self.ws = ws
    	self.recorder = recorder
    	self.isrunning = False
    	self.isSending = False
        self.THRES_VALUE = int(args.threshold)
        self.list_utt = None 
        self.saved = False
        self.args = args
        self.textbox = textbox

        
    def run(self):


        print "* Sender initialised !"
        self.isrunning = True

        while self.isrunning:

            # Waiting for a minimum of data available in the buffer
            while self.isrunning and len(self.recorder.buffer) < 5:
                time.sleep(0.001)

            # Checking if the condition (energetic) is respected
            
            while self.isSending:
                k = len(self.recorder.buffer) - 1
                if self.condition(k-1):
                    # Start of a new utterance
                    self.textbox["text"] = " O   "
                    indice_last_condition = k
                    utt = Utterance()
                    self.list_utt.add_utterance(utt)
                    self.list_utt.get_utt().set_start_utt_recording(self.recorder.time_recorded[k-1])
                    self.ws.set_utterance(self.list_utt.get_utt())
                    print "** Time start sending : ", time.strftime("%A %d %B %Y %H:%M:%S")

                    # Actual sending, k-1 because we want to have all the data of the beginning of the utterance
                    while self.isrunning and (self.condition(k-1) or self.condition(k) or self.condition(k+1))  and self.isSending:
                        if k < len(self.recorder.buffer)-2:
                            self.list_utt.get_utt().data.append(self.recorder.buffer[k-1])
                            self.ws.send_data(b''.join(self.recorder.buffer[k-1]))    
                            k+=1 

                    # Most of the time here because condition became false, end of the utterance
                    self.textbox["text"] = " X   "
                    self.ws.send_data(b''.join(self.recorder.buffer[k-1]))
                    self.ws.send_data(b''.join(self.recorder.buffer[k]))
                    self.ws.send_data(b''.join(self.recorder.buffer[k+1]))
                    self.list_utt.get_utt().data.append(self.recorder.buffer[k-1])
                    self.list_utt.get_utt().data.append(self.recorder.buffer[k])
                    self.list_utt.get_utt().data.append(self.recorder.buffer[k+1])
                    self.list_utt.get_utt().set_end_utt_recording(self.recorder.time_recorded[k-2])
                    
                    print "Nombre d'uttérances :", len(self.list_utt.list)
                    utt = None
                    print "** Time stop sending : ", time.strftime("%A %d %B %Y %H:%M:%S")

            if not self.saved:
                self.list_utt.generate_timed_transcript(self.recorder.filename,self.args)  
                self.list_utt.generate_timing(self.recorder.filename)
                # self.list_utt.generate_wav(self.recorder.filename)
                self.saved = True

                    
            
    def stop(self):
        self.isrunning = False

    def stop_sending(self) :
    	self.isSending = False

    def start_sending(self,list_utt):
        self.saved = False
    	self.isSending = True
        self.list_utt = list_utt

    # Simple function computing the energy of the audio signal to detect if there is speech or not
    def condition(self,k):

        if k > len(self.recorder.buffer) -1:
            return False

        #width=2 for format=paInt16 
        if audioop.rms(self.recorder.buffer[k],2) >= self.THRES_VALUE:
            return True
        return False

        # Testing purposes
        # if 150<k<250:
        #     return True
        # if 350<k<450:
        #     return True
        # if 550<k<750:
        #     return True
        # return False

    # Set the energy level considered as the minimum for speech
    def set_threshold(self,threshold):
        self.THRES_VALUE = threshold







