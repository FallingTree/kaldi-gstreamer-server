# -*- encoding: UTF-8 -*-
import threading 
import time




class Recorder_simulated(threading.Thread): 
    def __init__(self,args): 
        threading.Thread.__init__(self) 
        self.filename = args.wav
        self.buffer = []
        self.chunk = args.chunk
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.time_recorded = []
        self.filename = args.wav
        self.ispaused = False
        self.time_start_recording = 0

      
        
    def run(self): 
        print "* Recorder initialised"
        self.isrunning = True

        f=open(self.filename, "rb")
        temp = []
        for block in iter(lambda: f.read(self.chunk), ""):
            temp.append(block)

        while self.isrunning:          
            if self.recording and not self.ispaused:
                for block in temp:
                    self.time_recorded.append(time.time())
                    self.buffer.append(block)
                    time.sleep(self.chunk/self.rate)
                #print "Longueur du buffer : ", len(self.bufferc)

  
    def stop(self):
        self.isrunning = False 

    def pause(self):
        self.ispaused = True

    def restart(self):
        self.ispaused = False

    def stop_recoding(self):
        self.recording = False
        
    def start_recording(self):
        self.buffer = []
        self.time_start_recording = time.time()
        print "** Time starting recorder : ", time.strftime("%A %d %B %Y %H:%M:%S")
        self.recording = True

    def save_wav(self):
        # Opening the wav for saving the audio
        print "* No need to save Wav "+self.filename+" in mode simulation !"

        


        
