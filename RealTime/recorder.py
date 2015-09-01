# -*- encoding: UTF-8 -*-
import threading 
import time
import os
import pyaudio
import wave


class Recorder(): 
    def __init__(self,args): 
        self.stop = threading.Event()
        self.mythread = threading.Thread(target=self.run)
          

        self.p = pyaudio.PyAudio()
        self.buffer = []
        self.time_recorded = []
        self.chunk = args.chunk/2        
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.recording = False
        self.stream = None
        self.wf = None      
        self.filename = None
        self.ispaused = False
        self.time_start_recording = 0

        self.mythread.start()  

      
        
    def run(self): 
        print "* Recorder initialised"
        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk)
        
        while (not self.stop.is_set()):          
            if self.recording and not self.ispaused:
                self.time_recorded.append(time.time())
                data = self.stream.read(self.chunk)
                self.buffer.append(data)
                
            # print "Recording :", self.recording, "Alive :", not self.stop.is_set()

  
    def terminate(self):
        self.stop.set()
        
        self.buffer = []

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

        self.mythread.join(2)


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
