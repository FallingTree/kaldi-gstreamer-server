# -*- encoding: UTF-8 -*-
import threading 
import time
import os
import pyaudio
import wave


class Recorder(threading.Thread): 
    def __init__(self,args): 
        threading.Thread.__init__(self) 
        self.p = pyaudio.PyAudio()
        self.isrunning = False
        self.buffer = []
        self.time_recorded = []
        self.chunk = args.chunk        
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.stream = None
        self.wf = None      
        self.filename = None
        self.ispaused = False
        self.time_start_recording = 0

      
        
    def run(self): 
        print "* Recorder initialised"
        self.isrunning = True
        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)
        
        while self.isrunning:          
            if self.recording and not self.ispaused:
                self.time_recorded.append(time.time())
                data = self.stream.read(self.chunk)
                self.buffer.append(data)

  
    def stop(self):
        self.isrunning = False 
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

    def stop_recoding(self):
        self.recording = False

    def pause(self):
        self.ispaused = True

    def restart(self):
        self.ispaused = False
        
    def start_recording(self):
        self.buffer = []
        self.time_start_recording = time.time()
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
