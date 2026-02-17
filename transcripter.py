#!/usr/bin/env python
import logging
import numpy
import whisper

logger = logging.getLogger(__name__)

class Transcripter:
	"""
	Get waveforms from a fifo, transcript them and create command threads to process commands in background
	"""
	def __init__(self, segments_queue):
		self.segments_queue = segments_queue

		logger.info("Loading transcription model...")
		self.model = whisper.load_model("turbo")

	def run(self):
		while True:
			try:
				segment = self.segments_queue.pop()

				data_s16 = numpy.array(segment, dtype=numpy.int16)
				float_data = data_s16.astype(numpy.float32, order='C') / 32768.0
				result = self.model.transcribe(float_data)

				logger.info("got text: " + result["text"])
			except Exception as e:
				logger.error(e)
