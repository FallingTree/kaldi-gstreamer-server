# -*- encoding: UTF-8 -*-
import time
import threading
import wave
import audioop

class Sender(threading.Thread): 
    def __init__(self,ws,recorder,threshold):
    	threading.Thread.__init__(self) 
    	self.ws = ws
    	self.recorder = recorder
    	self.isrunning = False
    	self.isSending = False
    	self.num_seg = 0
        self.i = 0
        self.THRES_VALUE = int(threshold)
 
        
    def run(self):


        print "* Sender initialised !"
        self.isrunning = True

        while self.isrunning:
            while self.isrunning and len(self.recorder.buffer) < 5:
                time.sleep(0.001)

            k = len(self.recorder.buffer) - 2
            if self.condition(k) and self.isSending:
                indice_last_condition = k
                print "** Time start sending : ", time.strftime("%A %d %B %Y %H:%M:%S")
                self.ws.set_time_sent(time.time())
                while self.isrunning and self.condition(k) and self.isSending:
                    if k < len(self.recorder.buffer)-2:
                        self.ws.send_data(b''.join(self.recorder.buffer[k-1]))    
                        k+=1 
                print "** Time stop sending : ", time.strftime("%A %d %B %Y %H:%M:%S")
                wf = wave.open("data/wav_"+str(self.num_seg)+".wav", 'wb')
                wf.setnchannels(self.recorder.channels)
                wf.setsampwidth(self.recorder.p.get_sample_size(self.recorder.format))
                wf.setframerate(self.recorder.rate)
                wf.writeframes(b''.join(self.recorder.buffer[indice_last_condition:k]))
                wf.close()
                print "* Wav "+"data/wav_"+str(self.num_seg)+".wav saved !"
                self.num_seg+=1
                self.ws.set_nextSegment(self.num_seg)


            
  
    def stop(self):
        self.isrunning = False

    def stop_sending(self) :
    	self.isSending = False

    def start_sending(self):
    	self.isSending = True

# Simple fonction vérifiant le niveau d'énergie pour détecter ou non la présence de parole
    def condition(self,k):
        #width=2 for format=paInt16
        if audioop.rms(self.recorder.buffer[k],2) >= self.THRES_VALUE:
            return True

        return False

    def set_threshold(self,threshold):
        self.THRES_VALUE = threshold





