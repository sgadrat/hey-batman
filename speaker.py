import logging

logger = logging.getLogger(__name__)

class Speaker:
	"""
	Telling out loud a flow of sentences.
	"""
	def __init__(self, sentences_queue):
		self.sentences_queue = sentences_queue

	def run(self):
		logger.debug("running")
		while True:
			try:
				sentence = self.sentences_queue.pop()
				self.process_sentence(sentence)
			except Exception as e:
				logger.error(e)

	def process_sentence(self, sentence):
		"""
		Display and play a sentence.
		"""
		print(sentence)
		#TODO audio output, for now it only display sentences without playing it.
