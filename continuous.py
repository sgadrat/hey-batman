#!/usr/bin/env python

# Recording
import pyaudio
import wave
import math
import threading
import sys

# Transcribing
import whisper
import struct
import time
import numpy

# Pre-load transcription model
print("Loading transcription model...")
model = whisper.load_model("turbo")

# Input device selection
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512
RECORD_SECONDS = 10
device_index = 2
audio = pyaudio.PyAudio()

def transcribe(waveform):
	data_s16 = numpy.frombuffer(waveform, dtype=numpy.int16, count=len(waveform)//2, offset=0)
	float_data = data_s16.astype(numpy.float32, order='C') / 32768.0
	print(str(numpy.average(numpy.absolute(float_data))))
	if numpy.average(numpy.absolute(float_data)) < 0.005:
		print("<silence>")
	else:
		result = model.transcribe(float_data)
		print(result["text"])

print("----------------------record device list---------------------")
info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
pulse_id = None
for i in range(0, numdevices):
		if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			device_name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
			print("Input Device id ", i, " - ", device_name)
			if device_name.lower() == "pulse":
				pulse_id = i

print("-------------------------------------------------------------")

if pulse_id is not None:
	index = pulse_id
else:
	index = int(input())
print("recording via index "+str(index))

# Listening and transcribing
print("Press enter to start recording...", end="")
input()

stream = audio.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE, input=True,input_device_index = index,
	frames_per_buffer=CHUNK
)

try:
	while True:
		# bufferize some seconds of stream
		Recordframes = []
		for i in range(0, math.ceil(RATE / CHUNK * RECORD_SECONDS)):
			data = stream.read(CHUNK)
			Recordframes.append(data)

		waveform = b''.join(Recordframes)

		# Transcribe buffered audio
		threading.Thread(target=transcribe, args=(waveform,)).start()
finally:
	stream.stop_stream()
	stream.close()
	audio.terminate()
