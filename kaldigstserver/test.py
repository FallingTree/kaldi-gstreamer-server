import sys
import os
import pyaudio
import wave
import requests

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 600
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "temp.wav"
descripteur_wav = ['R', 'I', 'F', 'F', '$', 'X', '\x02', '\x00', 'W', 'A', 'V', 'E', 'f', 'm', 't', ' ', '\x10', '\x00', '\x00', '\x00', '\x01', '\x00', '\x01', '\x00', '\x80', '>', '\x00', '\x00', '\x00', '}', '\x00', '\x00', '\x02', '\x00', '\x10', '\x00', 'd', 'a', 't', 'a', '\x00', 'X']

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []


wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
    wf.writeframes(b''.join(data))



while True:
	try:		
	    data = stream.read(CHUNK)
	    frames.append(data)
	    wf.writeframes(b''.join(data))

		

	except KeyboardInterrupt:
		wf.close()
		sys.exit(0)

# tosend = list(frames)
# tosend[0] = (b''.join(descripteur_wav + list(frames[0])))

# payload = {'username': 'bob', 'email': 'bob@bob.com'}
# r = requests.put("http://somedomain.org/endpoint", data=payload)


