#!/usr/bin/env python
import logging
import pyaudio
import struct

logger = logging.getLogger(__name__)

class Listener:
	"""
	Read the mic and send non-silent sequences to a fifo.

	Glossary:
	  - sequence: a waveform of arbitrary length sent to the fifo (expectedly containing a sentence)
	  - segment: a waveform of fixed duration that represent the smallest unit of processing
	  - chunk: binary data of a segment

	  A sequence is made of multiple segments merged together.
	"""
	def __init__(self, output_queue):
		self.output_queue = output_queue
		self.silence_threshold = 400
		self.segment_duration = 0.25
		self.nb_silence_to_flush = 2

		self.sequence = []
		self.nb_silence = 0

	def _process(self, waveform):
		# Parse waveform and extract usful information
		waveform = struct.unpack(f"{len(waveform) // 2}h", waveform)
		sound_level = max(abs(min(waveform)), abs(max(waveform)))
		logger.debug(f"sound level: {sound_level}")

		# Select what to do of the waveform
		if sound_level < self.silence_threshold:
			# Silence:
			#  At the begining of a new sequence: ignore this waveform
			#  During a sequence with noise: append the silence, if there is two consecutive silences, call the sequence complete
			if len(self.sequence) > 0:
				logger.debug("appending silence")
				self.sequence += waveform
				self.nb_silence += 1
			else:
				logger.debug("ignoring silence")

			if self.nb_silence >= self.nb_silence_to_flush:
				logger.debug("flush sequence")
				self.output_queue.push(self.sequence)
				self.sequence = []
				self.nb_silence = 0
		else:
			# Noise: append to the current sequence, reset consecutive silence counter
			self.sequence += waveform
			self.nb_silence = 0

	def run(self, device = None):
		# Audio options
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 16000
		CHUNK = int(RATE * self.segment_duration)

		# Init audio capture object
		audio = pyaudio.PyAudio()

		# Select device to capture
		info = audio.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')
		device_id = device if isinstance(device, int) else None
		for i in range(0, numdevices):
			if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				device_name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
				print("Input Device id ", i, " - ", device_name)
				if isinstance(device, str) and device_name.lower() == device.lower():
					device_id = i

		if device_id is None:
			device_id = int(input("record device id: "))

		# Listen audio device
		print(f"Listening device #{device_id}")
		stream = audio.open(
			format = FORMAT,
			channels = CHANNELS,
			rate = RATE,
			input = True,
			input_device_index = device_id,
			frames_per_buffer = CHUNK
		)

		try:
			while True:
				# Read a segment of the waveform
				waveform = stream.read(CHUNK)

				# Process segment
				self._process(waveform)
		finally:
			stream.stop_stream()
			stream.close()
			audio.terminate()
