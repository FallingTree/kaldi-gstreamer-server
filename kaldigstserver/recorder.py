# -*- encoding: UTF-8 -*-
import threading 
import time
import os
import pyaudio
import wave



class Recorder(threading.Thread): 
    def __init__(self,rate,nom = ''): 
        threading.Thread.__init__(self) 
        self.nom = nom 
        self.p = pyaudio.PyAudio()
        self.isrunning = True
        self.buffer = []
        self.chunk = rate/8
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)
        self.state = 0



    def run(self): 
        self.state = 1
        
        while self.isrunning: 
            
            if self.recording:
                data = self.stream.read(self.chunk)
                self.buffer.append(data)
       
            #print "longueur du buffer", len(self.buffer)




    def stop(self):
        self.isrunning = False 
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def stop_recoding(self):
        self.recording = False 

    def start_recording(self):
        self.recording = True 


        
