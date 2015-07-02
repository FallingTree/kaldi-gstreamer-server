# -*- encoding: UTF-8 -*-
# Version avec thread pour chaque envoi de segment
# Ne marche pas car le serveur rejette les connexions si aucun décodeur n'est disponible
from Tkinter import *
from recorder import *
import time
import sys
import argparse
from ws4py.client.threadedclient import WebSocketClient
import threading
import sys
import urllib
import Queue
import json
import os

descripteur_wav = ['R', 'I', 'F', 'F', '$', 'X', '\x02', '\x00', 'W', 'A', 'V', 'E', 'f', 'm', 't', ' ', '\x10', '\x00', '\x00', '\x00', '\x01', '\x00', '\x01', '\x00', '\x80', '>', '\x00', '\x00', '\x00', '}', '\x00', '\x00', '\x02', '\x00', '\x10', '\x00', 'd', 'a', 't', 'a', '\x00', 'X']
WAVE_OUTPUT_FILENAME = "wav"
DATA_DIR = "tmp/wav"
global interface


class Sender(threading.Thread): 
    def __init__(self,frames,args,k): 
        threading.Thread.__init__(self) 
        self.frames = list(frames)
        self.args = args
        self.ws = None
        self.numero_wav = k


    def run(self): 
        global interface
        self.state = 1    

        self.ws = MyClient(self.frames, self.args.uri + '?%s' % (urllib.urlencode([("content-type", self.args.content_type)])), byterate=self.args.rate,
                                save_adaptation_state_filename=self.args.save_adaptation_state, send_adaptation_state_filename=self.args.send_adaptation_state)
        self.ws.connect()

        print "** Audio sample n°"+str(self.numero_wav)+" sent"

        result = self.ws.get_full_hyp()
        filename = DATA_DIR +'/'+WAVE_OUTPUT_FILENAME+'_'+str(self.numero_wav)

        print
        print "*** Final hypothesis for sample n°"+str(self.numero_wav)+" ****************"
        result = result.encode('utf-8')
        interface.TextArea.delete(interface.start_currTrans,"end")
        interface.TextArea.insert('end',result)
        interface.start_currTrans = interface.TextArea.index(INSERT)

        # On stocke le résultat dans un fichier pour pouvoir faire des calculs de WER
        fichier_ref = open(filename+'.trans', "w")
        fichier_ref.write(result)
        fichier_ref.close()
        print result
        print "**********************************************************"
        print



def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


class MyClient(WebSocketClient):

    def __init__(self, data, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.byterate = byterate
        self.final_hyp_queue = Queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.data = data

    #@rate_limited(4)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        #print "Socket opened!"
        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                print >> sys.stderr, "Sending adaptation state from %s" % self.send_adaptation_state_filename
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    print >> sys.stderr, "Failed to send adaptation state: ",  e

            for i in range(0,len(self.data)):
                self.send_data(b''.join(self.data[i]))


            print >> sys.stderr, "Audio sent, now sending EOS"
            #self.send("EOS")
            

        t = threading.Thread(target=send_data_to_ws)
        t.start()
        t.join()



    def received_message(self, m):
        global interface
        response = json.loads(str(m))
        #print >> sys.stderr, "RESPONSE:", response
        #print >> sys.stderr, "JSON was:", m
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    #print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    print >> sys.stderr, '\r%s' % trans.replace("\n", "\\n")
                else:
                    print_trans = trans.replace("\n", "\\n")
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]
                    interface.TextArea.insert('end',print_trans)
                    print >> sys.stderr, '\r%s' % print_trans,
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print >> sys.stderr, "Saving adaptation state to %s" % self.save_adaptation_state_filename
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            print >> sys.stderr, "Received error from server (status %d)" % response['status']
            if 'message' in response:
                print >> sys.stderr, "Error message:",  response['message']


    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        print "Websocket closed() called", code, reason
        #print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))


class Dictate(threading.Thread): 
    def __init__(self,args): 
        threading.Thread.__init__(self) 
        self.isrunning = True
        self.args = args

    def run(self): 
        global interface
        self.state = 1

        frames = []
        longueur_segment = int(interface.recorder.rate / interface.recorder.chunk * self.args.record_seconds)
        k=0

        while self.isrunning:
            while interface.isactif:

                # On verifie que que le buffer a eu assez de donnees pour pouvoir copier
                if len(interface.recorder.buffer) > interface.start_currSegment+longueur_segment+1:


                    # On copie la partie du buffer qui nous interesse
                    for i in range(0, longueur_segment):
                        frames.append(interface.recorder.buffer[interface.start_currSegment+i])

                    # On rajoute l'en-tête du fichier wav manuellement
                    temp = frames[0]
                    frames[0] = (b''.join(descripteur_wav + list(frames[0])))

                    # On envoi les données au serveur
                    t = Sender(frames,self.args,k)
                    t.start()

                    # Pour pouvoir l'écrire dans le wav on a pas besoin de l'en-tête
                    frames[0] = temp

                    # Ecriture dans un wav
                    filename = DATA_DIR +'/'+WAVE_OUTPUT_FILENAME+'_'+str(k)
                    wf = wave.open(filename+'.wav', 'wb')
                    wf.setnchannels(interface.recorder.channels)
                    wf.setsampwidth(interface.recorder.p.get_sample_size(interface.recorder.format))
                    wf.setframerate(interface.recorder.rate)
                    wf.writeframes(b''.join(frames))
                    wf.close()

                    print "* Wav n°"+str(k)+" enregistre"

                    interface.start_currSegment += longueur_segment
                    k+=1
                    frames = []
                
            while interface.isactif == False:
                time.sleep(0.5)




    def stop(self):
        self.isrunning = False





class Interface(Frame):
    
    """Notre fenêtre principale.
    Tous les widgets sont stockés comme attributs de cette fenêtre."""
    
    def __init__(self, fenetre, args, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.pack()

        self.title="ASR"

        # Création des frames
        self.frame1 = Frame(self, width=100, height=200, padx=10, pady=10)
        self.frame1.pack(side=RIGHT,fill=Y)

        self.frame2 = Frame(self,  width=400, height=10)
        self.frame2.pack(side=TOP, fill=X)

        self.frame3 = Frame(self, width=400, height=190, padx=10, pady=10)
        self.frame3.pack(side=LEFT,fill=Y)
        
        # Création de nos widgets
        self.bouton_quitter = Button(self.frame1, text="Quitter", command=self.cliquer_quit)
        self.bouton_quitter.pack(fill=X,pady=20)

        self.bouton_stop = Button(self.frame1, text="Stop", command=self.cliquer_stop)
        self.bouton_stop.pack(fill=X)

        bouton_record = Button(self.frame1, text="Record", command=self.cliquer_record)
        bouton_record.pack(fill=X)

        self.TextArea = Text(self.frame3)
        self.ScrollBar = Scrollbar(self.frame3)
        self.ScrollBar.config(command=self.TextArea.yview)
        self.TextArea.config(yscrollcommand=self.ScrollBar.set)
        self.ScrollBar.pack(side=RIGHT, fill=Y)
        self.TextArea.pack(expand=YES, fill=BOTH,side='bottom')        

        self.message = Label(self.frame2, text="Transcription : OFF")
        self.message.pack(side="left")

        self.transcript = ""
        self.start_currTrans = "1.0"
        self.recorder = Recorder(args.rate,'recorder') 
        self.start_currSegment = 0
        self.ws = None
        self.t = None
        self.isactif = False
        self.args = args

        


    
    def cliquer_record(self):

        if self.recorder.state == 0:
            self.recorder.start()
        self.recorder.start_recording()

        self.message["text"] = "Transcirition : ON"


        if self.isactif == False :
            self.isactif = True
            if self.t is None:
                self.t = Dictate(self.args)
                self.t.start()
        else:
            print "Déjà en cours"


    def cliquer_stop(self):
        self.isactif = False
        self.message["text"] = "Transcirition : OFF"

        if self.recorder is not None:
            self.recorder.buffer= []
            self.start_currSegment = 0
            self.recorder.stop_recoding()

        if self.ws is not None:
            self.ws.close()
            self.ws = None

    def cliquer_quit(self):
        
        self.cliquer_stop()

        if self.recorder is not None:
            self.recorder.stop()

        if self.t is not None:
            self.t.stop()

        self.quit()
        sys.exit(0)
        

        



def main():

    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri", help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int, help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('-d', '--duration', default=5, dest="record_seconds", type=int, help="Duration of each segment recorded in seconds") 
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='', help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    args = parser.parse_args()

    fenetre = Tk()
    fenetre.geometry("500x200")


    global interface
    interface = Interface(fenetre,args)
    interface.mainloop()
    interface.destroy()

if __name__ == '__main__':
    main()

