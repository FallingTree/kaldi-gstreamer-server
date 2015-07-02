# -*- encoding: UTF-8 -*-
import threading 
import time
import os
import pyaudio
import wave

descripteur_wav = ['R', 'I', 'F', 'F', '$', 'X', '\x02', '\x00', 'W', 'A', 'V', 'E', 'f', 'm', 't', ' ', '\x10', '\x00', '\x00', '\x00', '\x01', '\x00', '\x01', '\x00', '\x80', '>', '\x00', '\x00', '\x00', '}', '\x00', '\x00', '\x02', '\x00', '\x10', '\x00', 'd', 'a', 't', 'a', '\x00', 'X']

class Recorder(threading.Thread): 
    def __init__(self,rate): 
        threading.Thread.__init__(self) 
        self.p = pyaudio.PyAudio()
        self.isrunning = True
        self.buffer = []
        self.chunk = rate/8
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.stream = None
        self.state = 0

      
        
    def run(self): 
        self.state = 1

        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            #output=True,
            frames_per_buffer=self .chunk)
        
        i = 0
        while self.isrunning:          
            if self.recording:
                #print "Longueur buffer : ", len(self.buffer)
                data = self.stream.read(self.chunk)
                self.buffer.append(data)
                #self.stream.write(data)
                i+=1

            if i==1:
                # Ajout d'un descripteur de fichier wav
                self.buffer[0] = b''.join(descripteur_wav + list(self.buffer[0]))
            
    


    def stop(self):
        self.stop_recoding()
        self.isrunning = False 
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def stop_recoding(self):
        self.recording = False
        self.buffer = []

    def start_recording(self):
        self.recording = True 


        
