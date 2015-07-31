#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

from Tkinter import *
import tkFont
from recorder import *
from client import *
from sender import *
import time
import sys
import argparse
import os
import shutil
import pyaudio
import audioop
from utterance import *
from recorder_simulated import *
from VAD import *


# Class that manages the graphic interface
class Interface(Frame):
       
    def __init__(self, fenetre, args, **kwargs):
        self.fenetre = fenetre
        self.customFont = tkFont.Font(family="Helvetica", size=args.fontsize)
        self.fenetre.geometry(args.geometry)
        self.fenetre.title("ASR")
        self.fenetre.wm_attributes('-topmost', 1)

        Frame.__init__(self, self.fenetre, **kwargs)
        self.pack()

        # Création des frames
        self.frame1 = Frame(self, padx=10, pady=10)
        self.frame1.pack(side=RIGHT,fill=Y)

        self.frame2 = Frame(self)
        self.frame2.pack(side=TOP, fill=X)

        self.frame3 = Frame(self, padx=10, pady=10)
        self.frame3.pack(side=BOTTOM,fill=BOTH,expand=YES)
        
        # Création de nos widgets
        if args.control_condition == 'yes':
            self.bouton_condition = Button(self.frame2, text="O", command=self.cliquer_condition)
            self.bouton_condition.pack(fill=Y,side=LEFT)

        self.bouton_quitter = Button(self.frame1, text="Quitter", command=self.cliquer_quit)
        self.bouton_quitter.pack(fill=X,pady=20)

        self.bouton_pause = Button(self.frame1, text="Pause", command=self.cliquer_pause)
        self.bouton_pause.pack(fill=X)

        self.bouton_record = Button(self.frame1, text="Record", command=self.cliquer_record)
        self.bouton_record.pack(fill=X)

        self.bouton_set = Button(self.frame1, text="Set", command=self.cliquer_set)
        self.bouton_set.pack(fill=X)

        self.condition = Label(self.frame2, text=" X   ")
        self.condition.pack(side="left")

        self.message = Label(self.frame2, text="Transcription : OFF")
        self.message.pack(side="left")

        self.latence = Label(self.frame2, text="Subs Latence : undefined")
        self.latence.pack(side="right")


        self.TextArea = Text(self.frame3 ,font=self.customFont, wrap=WORD)
        self.ScrollBar = Scrollbar(self.frame3)
        self.ScrollBar.config(command=self.TextArea.yview)
        self.TextArea.config(yscrollcommand=self.ScrollBar.set)
        self.ScrollBar.pack(side=RIGHT, fill=Y)
        self.TextArea.pack(expand=YES, fill=BOTH,side='bottom')        
        self.isactif = False
        self.args = args
        self.threshold = 1000
        self.ispaused = False

    
    def cliquer_record(self):

        if self.isactif == False :

           # Objets gérant la transcription     
            content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(self.args.rate/2)  
            self.ws = MyClient(self.TextArea,self.latence, self.args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])), byterate=self.args.rate,
                              save_adaptation_state_filename=self.args.save_adaptation_state, send_adaptation_state_filename=self.args.send_adaptation_state)            
            if self.args.mode == 'live':
                self.recorder = Recorder(self.args)
            else:
                self.recorder = Recorder_simulated(self.args)

            self.recorder.start_recording()

            self.sender = Sender(self.ws,self.recorder,self.args,self.condition, self.message)
            try :
                self.ws.connect()
            except:
                self.ws.decoder_available = False

            self.sender.set_threshold(self.threshold)
            self.sender.start()

            if self.args.timing != '':
                self.VAD = VAD_manager(self.args,self.sender,self.recorder.time_start_recording,self)
                self.VAD.start()

            self.message["text"] = "Transcirition : ON"
            self.isactif = True           


            list_utt = List_utterance(self.recorder.time_start_recording)
            self.sender.start_sending(list_utt)
            self.bouton_record["text"] = "Stop"

            # Waiting if no decoder available to be able to get the message before closing
            time.sleep(5)

        else:
            self.cliquer_stop()
            self.bouton_record["text"] = "Record"


    def cliquer_stop(self):

        self.condition["text"] = " X   "
        if self.isactif:  

            self.sender.stop_sending()
            self.recorder.stop_recoding()
            time.sleep(1)         
            self.recorder.save_wav()


            # if self.recorder.mythread.isAlive():
            self.recorder.terminate()


            if self.sender.isAlive():
                self.sender.saved.wait()
                self.sender.stop()
                self.sender.join()


            self.sender = None
            self.ws = None
            self.recorder = None

            self.isactif = False
            self.message["text"] = "Transcirition : OFF"

            
    def cliquer_quit(self):
        self.cliquer_stop()
        self.quit()
        print "* Leaving"
        self.fenetre.destroy()
        sys.exit(0)

    # Function for setting the thresold level for speech recognition
    def cliquer_set(self):

        if self.isactif == False :
            if self.args.mode == 'live' :
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1200)

                frames = []
                print "* Recording speech sample"
                for i in range(0, int(16000 / self.args.chunk * 10)):
                    data = stream.read(self.args.chunk)
                    frames.append(data)


                print("* Done recording speech sample")

                stream.stop_stream()
                stream.close()
                p.terminate()

                p = None
                stream = None

                result = 0
                for chunk in frames:
                    result+=audioop.rms(chunk,2)
                result = result / len(frames)
                result+= -result/5

                print "Thresold level = ", result 
                self.threshold = result

            else:

                print "Not supported in simulation mode"


    def cliquer_pause(self):
        if self.isactif:
            if not self.ispaused:
                self.recorder.pause()
                self.sender.pause()
                self.bouton_pause["text"] = "Restart"
                self.ws.start_currTrans = self.TextArea.index('end')
                self.ispaused = True

            else:
                self.ispaused = False
                self.bouton_pause["text"] = "Pause"
                self.recorder.restart()
                self.sender.restart()

    def cliquer_condition(self):
        if self.isactif:
            self.sender.set_condition()
            if self.bouton_condition["text"] == "O":
                self.bouton_condition["text"] = "X"
            else:
                self.bouton_condition["text"] = "O"


def main():


    try:
        parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
        parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri", help="Server websocket URI default is ws://localhost:8888/client/ws/speech")
        parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int, help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
        parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
        parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
        parser.add_argument('--geometry', default="700x200", help="Size of the window, format : 700x200")
        parser.add_argument('-t','--threshold', default=2500, help="Min value of the rms of the audio which is considered as speech default is 2500 but it is recommended to use set at the beginning of a session")
        parser.add_argument('--mode', default='live', help="simulation or live")
        parser.add_argument('--subs', default='no', help="yes or no. At the end all the utterances are sent again in order to have a real-timed transcript and timing for decoding but can be long")
        parser.add_argument('-w', '--wav', default='', help="Wav for simulation mode")
        parser.add_argument('-f', '--fontsize', default=20, help="Font size of the subs, default is 20")
        parser.add_argument('-c', '--control_condition', default="no", help="yes or no. If yes a button allows to control whether or not the condition for VAC is set or not")
        parser.add_argument('--chunk', default=1200, help="Size of the chunk for the recording")
        parser.add_argument('--timing', default='', help="Timing file for automatic decision about presence or speech or not")

        args = parser.parse_args()
        args.chunk=int(args.chunk)

        if args.timing != '':
            if not os.path.exists(args.timing):
                print "Timing file do not exists"
                exit()

        if args.mode=='simulation':
            if not os.path.exists(args.wav):
                print "Wav do not exists"
                exit()

        if args.wav != '' and args.mode =='live':
            print "If you want to use a wav for the audio input use simulation mode"
            print "option --mode simulation"
            exit()

        if not (args.mode == 'simulation' or args.mode == 'live'):
            print "Mode not recognised"
            exit()

        if not os.path.exists('data'):   
            os.makedirs('data')

        if not os.path.exists('tmp'):   
            os.makedirs('tmp')

        fenetre = Tk() 
        interface = Interface(fenetre,args)

        def on_closing():
            interface.cliquer_quit()

        fenetre.protocol("WM_DELETE_WINDOW", on_closing)

        interface.mainloop()



    except KeyboardInterrupt:
        interface.cliquer_quit()
        exit(0)



if __name__ == '__main__':
    main()
