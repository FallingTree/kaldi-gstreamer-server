import time
import threading

# A simple class to manage an utterance with the timing to generate a trs file
class Utterance:
	
	def __init__(self):
		self.transcript = ""
		self.time_start_record = 0
		self.time_end_record = 0
		self.time_start_sending = 0
		self.time_end_sending = 0
		self.time_first_result = 0
		self.time_final_result = 0
		self.event_end = threading.Event()
		self.event_end_recording = threading.Event()
		self.event_got_final_result = threading.Event()

	def set_start_utt_recording(self,recorder_time_data):
		self.time_start_sending=time.time()
		self.time_start_record=recorder_time_data
    	
	def set_end_utt_recording(self,recorder_time_data):
		self.time_end_sending=time.time()
		self.time_end_record=recorder_time_data
		self.event_end_recording.set()

	def set_first_result(self):
		self.time_first_result=time.time()

	def set_final_result(self):
		self.time_final_result=time.time()
		
	def set_transcript(self,transcript):
		self.transcript += transcript

	def set_end_utt(self):
 		self.event_end.set()

	def set_got_final_result(self):
		self.event_got_final_result.set()

	def wait_final_result(self,k):
		if k==0:
			self.event_got_final_result.wait()
		else:
			self.event_got_final_result.wait(k)

	def wait_end_utt_recording(self):
		self.event_end_recording.wait()
		

	def wait_end_utt(self):
		self.event_end.wait()

	def get_latence(self):
		return self.time_first_result - self.time_start_record

class List_utterance(object):
	def __init__(self,time_recording_begin):
		super(List_utterance, self).__init__()
		self.list = []
		self.time_recording_begin = time_recording_begin

	def add_utterance(self,utterance):
		self.list.append(utterance)

	def generate_transcript(self,filename):
		transcript = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
		transcript+= "<!DOCTYPE Trans SYSTEM \"trans-14.dtd\">\n"
		transcript+= "<Trans scribe=\"ASR\" audio_filename="+filename+".wav version=\"4\" version_date="+time.strftime("%y%m%d")+" xml:lang=\"French\">\n"
		for utterance in self.list:
			transcript+="\n<Sync time="+str(utterance.time_start_record-self.time_recording_begin)+"/>\n"
			transcript+=utterance.transcript
			transcript+="\n<Sync time="+str(utterance.time_end_record-self.time_recording_begin)+"/>\n"
		
		fichier_trs = open(filename+'.trs', "a")
		fichier_trs.write(transcript)
		fichier_trs.close()

		print" * TRS saved"

	def generate_timing(self,filename):
		chaine = "time_start_record;time_end_record;time_start_sending;time_end_sending;time_first_result;self.time_final_result\n"

		for utterance in self.list:
			chaine+=str(utterance.time_start_record)+';'+str(utterance.time_end_record)+';'+\
						str(utterance.time_start_sending)+';'+str(utterance.time_end_sending)+';'+\
						str(utterance.time_first_result)+';'+str(utterance.time_final_result)+'\n'

		fichier_timing = open(filename+'.txt', "a")
		fichier_timing.write(chaine)
		fichier_timing.close()

		print "* Timing saved"
			


		

