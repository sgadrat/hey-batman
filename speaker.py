# play audio
import pyaudio
import numpy

# text to speech
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# misc
import logging

logger = logging.getLogger(__name__)

class Speaker:
	"""
	Telling out loud a flow of sentences.
	"""
	def __init__(self, sentences_queue):
		self.sentences_queue = sentences_queue

		self.model = Qwen3TTSModel.from_pretrained(
			#"Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
			"Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
			device_map="cuda:0",
			dtype=torch.bfloat16,
			#attn_implementation="flash_attention_2", # needs to be installed
		)

		self.sample_width = 2
		self.pyaudio = pyaudio.PyAudio()
		self.audio_stream = self.pyaudio.open(
			format=self.pyaudio.get_format_from_width(self.sample_width),
			channels=1,
			rate=24000,
			output=True
		)

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
		# Display sentence
		print(sentence)

		# Play sentence
		wavs, sr = self.model.generate_custom_voice(
			text=sentence,
			language="English", # Pass `Auto` (or omit) for auto language adaptive; if the target language is known, set it explicitly.
			speaker="Ryan",
			instruct="", # Omit if not needed.
		)
		sample_bits = 8 * self.sample_width
		sample_max_value = 2 ** (sample_bits - 1)
		s16_data = (wavs[0] * sample_max_value).astype(numpy.int16)
		self.audio_stream.write(s16_data.tobytes())
