# -*- encoding: UTF-8 -*-
import threading 
import time
import pyaudio




class Recorder_simulated(): 
    def __init__(self,args): 
        self.stop = threading.Event()
        self.mythread = threading.Thread(target=self.run)

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

        self.p = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.channels = 1
        self.stream = None

        self.mythread.start()


      
        
    def run(self): 
        print "* Recorder initialised"


        f=open(self.filename, "rb")

        self.stream = self.p.open(format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk)

        while (not self.stop.is_set()):          
            while not self.recording and (not self.stop.is_set()):
                time.sleep(0.1)

            block = f.read(self.chunk)
            self.time_recorded.append(time.time())
            self.buffer.append(block)
            self.stream.write(block)
            while block != "" and (not self.stop.is_set()):
                block = f.read(self.chunk)
                if self.recording and not self.ispaused:
                    self.time_recorded.append(time.time())
                    self.buffer.append(block)
                    self.stream.write(block)
                    #time.sleep(self.chunk/self.rate)

                #print "Longueur du buffer : ", len(self.bufferc)
            


        print "* Stopping recorder"
        f.close()

  
    def terminate(self):
        self.stop.set()
        
        self.buffer = []

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()


        self.mythread.join()


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

        


        
