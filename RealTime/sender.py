# -*- encoding: UTF-8 -*-
import time
import threading
import wave
import audioop
from utterance import Utterance

class Sender(threading.Thread): 
    def __init__(self,ws,recorder,args,textbox,message):
    	threading.Thread.__init__(self) 
    	self.ws = ws
    	self.recorder = recorder
    	self.isrunning = False
    	self.isSending = False
        self.THRES_VALUE = int(args.threshold)
        self.list_utt = None 
        self.saved = threading.Event()
        self.args = args
        self.textbox = textbox
        self.ispaused = False
        self.condition_set = False
        self.condition_False = False
        self.condition_True = False
        self.message = message


        
    def run(self):


        print "* Sender initialised !"
        self.isrunning = True

        while self.isrunning:

            # Waiting for a minimum of data available in the buffer
            while self.isrunning and len(self.recorder.buffer) < 5:
                time.sleep(0.01)

            # If no decoder available ending here
            if not self.ws.decoder_available:
                self.isSending = False
                self.isrunning = False
                self.saved.set()
                self.message["text"] = "No decoder Available !  "

            # Checking if the condition (energetic) is respected
            
            while self.isSending:
                k = len(self.recorder.buffer) - 1
                if self.condition(k):
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
                        if k < len(self.recorder.buffer)-1:
                            self.list_utt.get_utt().data.append(self.recorder.buffer[k-1])
                            self.ws.send_data(b''.join(self.recorder.buffer[k-1]))    
                            k+=1 
                    print "** Time stop sending : ", time.strftime("%A %d %B %Y %H:%M:%S")
                    # Most of the time here because condition became false, end of the utterance
                    if self.isSending:
                        self.textbox["text"] = " X   "
                    self.ws.send_data(b''.join(self.recorder.buffer[k-1]))
                    self.list_utt.get_utt().data.append(self.recorder.buffer[k-1])
                    self.list_utt.get_utt().set_end_utt_recording(self.recorder.time_recorded[k])
                    
                    print "* Number of uttérances :", len(self.list_utt.list)
                    utt = None
                    

            if not self.saved.isSet():
                self.ws.send("EOS")
                time.sleep(6)
                self.list_utt.generate_timed_transcript(self.recorder.filename,self.args)            
                self.saved.set()



                    
            
    def stop(self):
        self.isrunning = False

    def pause(self):
        self.ispaused = True

    def restart(self):
        self.ispaused = False

    def force_condition_false(self):
        self.condition_False = True
        self.condition_True = False

    def force_condition_true(self):
        self.condition_False = False
        self.condition_True = True

    def stop_sending(self) :
    	self.isSending = False

    def set_condition(self) :
        self.condition_set = not self.condition_set

    def start_sending(self,list_utt):
        self.saved.clear()
    	self.isSending = True
        self.list_utt = list_utt

    # Simple function computing the energy of the audio signal to detect if there is speech or not
    def condition(self,k):

        if self.condition_False:
            return False

        if self.condition_True:
            return True

        if self.ispaused:
            return False

        if self.args.control_condition == 'yes':
            return self.condition_set

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







