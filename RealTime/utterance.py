import time
import threading
import wave
import pyaudio
from client_transcript import *

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
		self.data = []
		self.event_end = threading.Event()
		self.event_end_recording = threading.Event()
		self.event_got_final_result = threading.Event()
		self.event_started = threading.Event()

	def set_start_utt_recording(self,recorder_time_data):
		self.time_start_sending=time.time()
		self.time_start_record=recorder_time_data
		self.event_started.set()
    	
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
		transcript+= "<Trans scribe=\"ASR\" audio_filename=\""+str(filename)+"\" version=\"4\" version_date=\""+str(time.strftime("%y%m%d"))+"\" xml:lang=\"French\">\n"
		transcript+= "<Episode>\n<Section type=\"report\" startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
		transcript+= "<Turn startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
		for utterance in self.list:
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_start_record-self.time_recording_begin)
			transcript+=utterance.transcript
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_end_record-self.time_recording_begin)
		transcript+="\n</Turn>\n</Section>\n</Episode>\n</Trans>"
		fichier_trs = open("data/"+filename+'.trs', "a")
		fichier_trs.write(transcript)
		fichier_trs.close()

		print" * TRS saved"

	def generate_timing(self,filename):
		chaine = "time_start_record;time_end_record;time_start_sending;time_end_sending;time_first_result;self.time_final_result\n"

		for utterance in self.list:
			chaine+=str(utterance.time_start_record)+';'+str(utterance.time_end_record)+';'+\
						str(utterance.time_start_sending)+';'+str(utterance.time_end_sending)+';'+\
						str(utterance.time_first_result)+';'+str(utterance.time_final_result)+'\n'

		fichier_timing = open("data/"+filename+'.txt', "a")
		fichier_timing.write(chaine)
		fichier_timing.close()

		print "* Timing saved"

	def generate_wav(self,filename):
		print "* Generating Wav"
		i=1
		for utterance in self.list:
			wf = wave.open('tmp/'+filename+'_'+str(i)+'.wav', 'wb')
			wf.setnchannels(1)
			wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
			wf.setframerate(16000)
			wf.writeframes(b''.join(utterance.data))
			wf.close()
			print "     Wav "+str(i)+" saved !"
			i+=1

		print "* Wav generated"

	def generate_timed_transcript(self,filename,args):
		transcript = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
		transcript+= "<!DOCTYPE Trans SYSTEM \"trans-14.dtd\">\n"
		transcript+= "<Trans scribe=\"ASR\" audio_filename=\""+str(filename)+"\" version=\"4\" version_date=\""+str(time.strftime("%y%m%d"))+"\" xml:lang=\"French\">\n"
		transcript+= "<Episode>\n<Section type=\"report\" startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
		transcript+= "<Turn startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)

		time.sleep(2)
		for utterance in self.list:
			content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(args.rate/2)
			ws = MyClient_trans(utterance.data, args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])), byterate=args.rate,
					save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)
			ws.connect()
			result = ws.get_full_hyp()
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_start_record-self.time_recording_begin)
			transcript+=result.encode('utf-8')
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_end_record-self.time_recording_begin)
			ws = None
			time.sleep(1.5)
		transcript+="\n</Turn>\n</Section>\n</Episode>\n</Trans>"
		fichier_trs = open("data/"+filename+'_timed.trs', "a")
		fichier_trs.write(transcript)
		fichier_trs.close()

		print" * TRS saved"
			


		

