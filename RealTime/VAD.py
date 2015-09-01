import time
import threading

class VAD_manager(threading.Thread): 
    def __init__(self,args,sender,time_start_recording,interface): 
        threading.Thread.__init__(self) 
        self.isrunning = False
        self.file_timing = args.timing
        self.sender = sender
        self.time_start_recording = time_start_recording
        self.interface = interface

      
    def run(self): 

        liste_time_start_recording = []
        liste_time_end_recording = []
        with open(self.file_timing) as f: # open the file for reading
            i=1
            for line in f: # iterate over each line
                if i>1:
                    time_start_recording, time_end_recording, time_record_send, time_sending, time_first_result, time_final_result, transcript = line.split(';') # split it by whitespace
                    time_end_recording= float(time_end_recording)
                    time_start_recording = float(time_start_recording) 

                    liste_time_start_recording.append(time_start_recording)
                    liste_time_end_recording.append(time_end_recording)

                i+=1

        self.sender.force_condition_false()
        time.sleep(liste_time_start_recording[0])
        self.sender.force_condition_true()
        time.sleep(liste_time_end_recording[0]-liste_time_start_recording[0])
        self.sender.force_condition_false()
        for x in xrange(1,len(liste_time_end_recording)-1):
            time.sleep(liste_time_start_recording[x]-liste_time_end_recording[x-1])
            self.sender.force_condition_true()
            time.sleep(liste_time_end_recording[x]-liste_time_start_recording[x])
            self.sender.force_condition_false()

        time.sleep(3)
        self.interface.cliquer_quit()


    def stop():
        self.isrunning = False

