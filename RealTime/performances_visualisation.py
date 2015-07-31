#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
from pylab import *
import numpy as np
import matplotlib.pyplot as p
import matplotlib.patches as patches
import os
from os import walk
import sys
import argparse




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

	parser = argparse.ArgumentParser(description='Command line client for performaces visualisation')
	parser.add_argument('-d', '--directory', default="data", help="Data directory")
	args = parser.parse_args()

	if not os.path.exists(args.directory):
		print "* No data repertory found !"
		exit()

	f = []
	for (dirpath, dirnames, filenames) in walk(args.directory):
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
			with open(args.directory+'/'+files) as f: # open the file for reading
				i=1
				for line in f: # iterate over each line
					if i>1:
						time_start_recording, time_end_recording, time_record_send, time_sending, time_first_result, time_final_result, transcript = line.split(';') # split it by whitespace
						record_length = float(time_end_recording) - float(time_start_recording) # convert from string to float
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

	fig1 = p.figure(1)
	yticks = np.arange(0, max(liste_time_final_result),2)
	a,=p.plot(liste_length_record,color="blue", linewidth=1.0, linestyle="--", marker='o')
	b,=p.plot(liste_time_record_send,color="red", linewidth=1.0, linestyle="--", marker='x')
	c,=p.plot(liste_time_sending,color="green", linewidth=1.0, linestyle="--",marker='p')
	d,=p.plot(liste_time_first_result,color="orange", linewidth=1.0, linestyle="--",marker='s')
	e,=p.plot(liste_time_final_result,color="black", linewidth=1.0, linestyle="--",marker='D')
	p.legend([a,b,c,d,e],['Length record','Time record-send','Time sending','Latency','Time final result'])
	p.fill_between(np.arange(0.0,len(liste_time_first_result)),0,liste_time_first_result, facecolor='orange', alpha=0.5)

	textstr = "Mean subs Latency = %2f s" %(sum(liste_time_first_result)/len(liste_time_first_result))
	p.text(2, max(liste_time_final_result), textstr, color="white",
			bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
	#p.yticks(yticks)
	p.xlabel("Utterance")
	p.ylabel("Temps (s)")
	p.title("Performances ASR")
	

	fig2 = p.figure(2)
	b,=p.plot(liste_length_record,liste_time_record_send,color="red", linewidth=1.0, linestyle="", marker='x',)
	c,=p.plot(liste_length_record,liste_time_sending,color="green", linewidth=1.0, linestyle="",marker='p')
	d,=p.plot(liste_length_record,liste_time_first_result,color="orange", linewidth=1.0, linestyle="",marker='s',markersize=5)
	e,=p.plot(liste_length_record,liste_time_final_result,color="black", linewidth=1.0, linestyle="",marker='D')
	p.legend([b,c,d,e],['Time record-send','Time sending','Latency','Time final result'])
	p.xlabel('Length record (s)')
	p.ylabel("Temps (s)")
	p.title("Performances ASR")
	p.text(2, max(liste_time_final_result), textstr, color="white",
			bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
	p.show()


if __name__ == '__main__':
	main()