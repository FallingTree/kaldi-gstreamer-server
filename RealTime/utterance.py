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
		self.time_start_sending_end = 0
		self.time_end_sending_end = 0
		self.time_first_result_end = 0
		self.time_final_result_end = 0

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

	def get_len(self):
		return len(self.list)

	def get_utt(self):
		return self.list[len(self.list)-1]

	def generate_transcript(self,filename,args):
		transcript = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
		transcript+= "<!DOCTYPE Trans SYSTEM \"trans-14.dtd\">\n"
		transcript+= "<Trans scribe=\"ASR\" audio_filename=\""+str(filename)+"\" version=\"4\" version_date=\""+str(time.strftime("%y%m%d"))+"\" xml:lang=\"French\">\n"
		transcript+= "<Episode>\n<Section type=\"report\" startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
		transcript+= "<Turn startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
		print "* Now sending utterance by utterance for full results"
		utterances_left = len(self.list)
		for utterance in self.list:
			print "* Now treating utterance ", len(self.list)-utterances_left+1, "Left : ", utterances_left
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_start_record-self.time_recording_begin)
			transcript+=utterance.transcript
			transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_end_record-self.time_recording_begin)
			utterances_left+=-1
		transcript+="\n</Turn>\n</Section>\n</Episode>\n</Trans>"

		if args.mode == "simulation":
			fichier_trs = open(filename.split('.')[0]+'_simulation.trs', "a")
		else:
			fichier_trs = open("data/"+filename+'.trs', "a")
		fichier_trs.write(transcript)
		fichier_trs.close()

		print"* TRS saved"

	def generate_timing(self,filename,args):
		chaine = "time_start_record;time_end_record;time_start_sending;time_end_sending;time_first_result;self.time_final_result\n"

		for utterance in self.list:
			chaine+=str(utterance.time_start_record)+';'+str(utterance.time_end_record)+';'+\
						str(utterance.time_start_sending)+';'+str(utterance.time_end_sending)+';'+\
						str(utterance.time_first_result)+';'+str(utterance.time_final_result)+'\n'

		if args.mode == "simulation":
			fichier_timing = open(filename.split('.')[0]+'_live_simulation.txt', "a")
			fichier_timing.write(chaine)
			fichier_timing.close()
		else:
			fichier_timing = open("data/"+filename+'_live.txt', "a")
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
		if len(self.list) > 0:
			if args.subs == 'yes':
				transcript = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
				transcript+= "<!DOCTYPE Trans SYSTEM \"trans-14.dtd\">\n"
				transcript+= "<Trans scribe=\"ASR\" audio_filename=\""+str(filename)+"\" version=\"4\" version_date=\""+str(time.strftime("%y%m%d"))+"\" xml:lang=\"French\">\n"
				transcript+= "<Episode>\n<Section type=\"report\" startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)
				transcript+= "<Turn startTime=\"0\" endTime=\"%.3f\">\n" % (self.list[len(self.list)-1].time_end_record-self.time_recording_begin)

				chaine = "time_start_record;time_end_record;time_record_send;time_sending;time_first_result;time_final_result;transcript\n"	
				print "* Now sending utterance by utterance for full results"
				utterances_left = len(self.list)
				for utterance in self.list:	
					print "* Now treating utterance ", len(self.list)-utterances_left+1, "Left : ", utterances_left
					ref_time = time.time()
					content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" %(args.rate/2)
					ws = MyClient_trans(args.chunk, utterance, args.uri + '?%s' % (urllib.urlencode([("content-type", content_type)])), byterate=args.rate,
							save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state)
					ws.connect()
					result = ws.get_full_hyp()
					utterance.time_final_result_end = time.time()

					transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_start_record-self.time_recording_begin)
					transcript+=result.encode('utf-8')
					transcript+="\n<Sync time=\"%.3f\" />\n" %(utterance.time_end_record-self.time_recording_begin)

					if result.encode('utf-8') != '':
						chaine+= str(utterance.time_start_record-self.time_recording_begin)+';'+str(utterance.time_end_record-self.time_recording_begin)+';'+str(utterance.time_start_sending-utterance.time_start_record )+\
						';'+str(utterance.time_end_sending_end-utterance.time_start_sending_end)+';'+\
							str(utterance.time_first_result_end-ref_time)+';'+str(utterance.time_final_result_end-ref_time)+'; '+result.encode('utf-8')+'\n'

					ws = None				
					time.sleep(1.5)
					utterances_left+=-1
					print

				transcript+="\n</Turn>\n</Section>\n</Episode>\n</Trans>"
				if args.mode == 'simulation':
					fichier_trs = open(filename.split('.')[0]+"_simulation.trs", "a")
					fichier_trs.write(transcript)
					fichier_trs.close()
				else:
					fichier_trs = open("data/"+filename+'_timed.trs', "a")
					fichier_trs.write(transcript)
					fichier_trs.close()
				print "* TRS real timed saved"

				if args.mode == 'simulation':
					fichier_timing_utt_per_utt = open(filename.split('.')[0]+'_utt_per_utt_simulation_chunk'+str(args.chunk)+'.txt', "a")
					fichier_timing_utt_per_utt.write(chaine)
					fichier_timing_utt_per_utt.close()
				else:
					fichier_timing_utt_per_utt = open("data/"+filename+'_utt_per_utt.txt', "a")
					fichier_timing_utt_per_utt.write(chaine)
					fichier_timing_utt_per_utt.close()
				print "* Timing utt per utt saved"


			else:
				self.generate_transcript(filename,args)

			
			


		

