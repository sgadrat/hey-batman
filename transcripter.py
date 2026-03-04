#!/usr/bin/env python
import logging
import numpy
import whisper

logger = logging.getLogger(__name__)

class Transcripter:
	"""
	Get waveforms from a fifo, transcript them and create command threads to process commands in background
	"""
	def __init__(self, sequences_queue, sentences_queue, task="transcript"):
		self.sequences_queue = sequences_queue
		self.sentences_queue = sentences_queue

		logger.info("Loading transcription model...")
		self.decode_options = {
			"task": task, # May be transcribe to output original language
			"language": None, # Original language as two-letters code (or None to auto-detect)
		}
		model_name = {
			"transcript": "turbo",
			"translate": "large-v3",
		}[self.decode_options["task"]]
		self.model = whisper.load_model(model_name)

	def run(self):
		while True:
			try:
				sequence = self.sequences_queue.pop()

				data_s16 = numpy.array(sequence, dtype=numpy.int16)
				float_data = data_s16.astype(numpy.float32, order='C') / 32768.0
				result = self.model.transcribe(float_data, **self.decode_options)

				logger.info(f"got text: {result['text']}")
				self.sentences_queue.push(result["text"])
			except Exception as e:
				logger.error(e)
