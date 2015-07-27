#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
from pylab import *
import matplotlib.pyplot as p
import os
from os import walk
import sys



class timing_utterance(object):
	"""Simple class to store de data of the utterance"""
	def __init__(self, record_length, time_record_send,time_sending, time_first_result, time_final_result, transcript):
		super(timing_utterance, self).__init__()
		self.record_length = record_length
		self.time_first_result = time_first_result 
		self.time_final_result = time_final_result
		self.transcript = transcript
		self.time_record_send = time_record_send
		self.time_sending = time_sending
		self.nb_mots = len(transcript.split())
	def visualize(self):
		print self.record_length,';',self.time_record_send,';',self.time_sending,';',self.time_first_result,';',self.time_final_result,';',self.transcript

		

def main():

	if not os.path.exists('data'):
		print "* No data repertory found !"
		exit()

	f = []
	for (dirpath, dirnames, filenames) in walk('data'):
		f.extend(filenames)
		break

	liste = []
	liste_length_record = []
	liste_time_record_send = []
	liste_time_sending = []
	liste_time_first_result = []
	liste_time_final_result = []

	for files in f:
		if files.split('.')[1] == 'txt':
			list_utterance = []
			filename = ''
			with open('data/'+files) as f: # open the file for reading
				i=1
				for line in f: # iterate over each line
					if i>1:
						record_length, time_record_send, time_sending, time_first_result, time_final_result, transcript = line.split(';') # split it by whitespace
						record_length = float(record_length) # convert from string to float
						time_record_send = float(time_record_send)
						time_sending = float(time_sending)
						time_first_result = float(time_first_result)
						time_final_result = float(time_final_result)
						utt = timing_utterance(record_length, time_record_send, time_sending, time_first_result, time_final_result, transcript)
						
						list_utterance.append(utt)

						liste_length_record.append(record_length)
						liste_time_record_send.append(time_record_send)
						liste_time_sending.append(time_sending)
						liste_time_first_result.append(time_first_result)
						liste_time_final_result.append(time_final_result)
					i+=1
			liste.extend(list_utterance)		

			print "Recorded ", files.split('.')[0].split('_')[1], files.split('.')[0].split('_')[2], ':'
			print "record_length; time-record_send; time_sending; time_first_result; time_final_result; transcript"
			print "*****************************************************************************************************"
			for utterance in list_utterance:
				utterance.visualize()



	a,=p.plot(liste_length_record,color="blue", linewidth=1.0, linestyle="-")
	b,=p.plot(liste_time_record_send,color="red", linewidth=1.0, linestyle="-")
	c,=p.plot(liste_time_sending,color="green", linewidth=1.0, linestyle="-")
	d,=p.plot(liste_time_first_result,color="orange", linewidth=1.0, linestyle="-")
	e,=p.plot(liste_time_final_result,color="black", linewidth=1.0, linestyle="-")
	p.legend([a,b,c,d,e],['Length record','Time record-send','Time sending','Latency','Time final result'])
	p.xlabel("Utterance")
	p.ylabel("Temps (s)")
	p.title("Performances ASR")
	p.show()


if __name__ == '__main__':
	main()