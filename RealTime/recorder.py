# -*- encoding: UTF-8 -*-
import threading 
import time
import os
import pyaudio
import wave


class Recorder(threading.Thread): 
    def __init__(self,rate): 
        threading.Thread.__init__(self) 
        self.p = pyaudio.PyAudio()
        self.isrunning = False
        self.buffer = []
        self.chunk = 1200
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.stream = None
        self.wf = None
        self.time_recorded = []
        self.filename = None

      
        
    def run(self): 
        print "* Recorder initialised"
        self.isrunning = True
        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)
        
        while self.isrunning:          
            if self.recording:
                data = self.stream.read(self.chunk)
                self.buffer.append(data)
                self.time_recorded.append(time.time())

                #print "Longueur du buffer : ", len(self.bufferc)

  
    def stop(self):
        self.isrunning = False 
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def stop_recoding(self):
        self.recording = False
        
    def start_recording(self):
        self.buffer = []
        print "** Time starting recorder : ", time.strftime("%A %d %B %Y %H:%M:%S")
        self.recording = True
        self.filename = "record_"+time.strftime("%d-%m-%Y_%H-%M-%S")

    def save_wav(self):
        # Opening the wav for saving the audio

        self.wf = wave.open("data/"+self.filename+".wav", 'wb')
        self.wf.setnchannels(self.channels)
        self.wf.setsampwidth(self.p.get_sample_size(self.format))
        self.wf.setframerate(self.rate)
        self.wf.writeframes(b''.join(self.buffer))
        self.wf.close()
        print "* Wav "+self.filename+" saved !"

        


        
