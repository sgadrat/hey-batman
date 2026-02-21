import logging
import pathlib
import re
import subprocess
import threading
import unicodedata
import yaml

logger = logging.getLogger(__name__)

class ActionLauncher:
	def __init__(self, starters, sentences_queue):
		self.starters = [self.normalize(starter) for starter in starters]
		self.sentences_queue = sentences_queue
		self.actions = []

	def run(self):
		logger.debug("running")
		while True:
			try:
				sentence = self.sentences_queue.pop()
				self.process_sentence(sentence)
			except Exception as e:
				logger.error(e)

	def load_actions(self, actions_path):
		# Load actions definitions
		with open(actions_path, "r") as actions_file:
			self.actions = yaml.load(actions_file, Loader=yaml.CLoader)

		# Resolve relative paths
		basedir = pathlib.Path(actions_path).parent
		for action in self.actions:
			action["script"] = pathlib.Path(action["script"])
			if not action["script"].is_absolute():
				action["script"] = (basedir / action["script"]).absolute()

	def normalize(self, text):
		"""
		Normalize a string by removing accents, diacritics and lower-casing it.

		Note: produced string has the same length than the original, characters can
		      be altered but are at the same position as in the original string.
		"""
		normalized = unicodedata.normalize('NFKD', text)
		normalized = u"".join([c for c in normalized if not unicodedata.combining(c)])
		normalized = normalized.lower()
		logger.debug(f"normalize({text}) -> `{normalized}`")
		return normalized

	def process_sentence(self, sentence):
		"""
		Extract an action from a sentence and execute it.

		A sentence is a series of words pronounced in one go by the user, we interprete is as begin formed like that:
		  - "<garbage> <starter> <command> <parameters>"

		garbage: possible noises we do not care about
		starter: a starter expression (like the famous "ok google")
		command: a series of words indicating the action to take
		parameters: the rest of the sentence

		Example:
			"[music playing] hey robot! open      firefox"
			"<garbage      > <starter>  <command> <parameters>"
		"""
		logger.debug(f"Processing sentence: `{sentence}`")
		def next_word(text, pos):
			while pos < len(text) and not text[pos].isalpha():
				pos += 1

			if pos >= len(text):
				return ""

			return text[pos:]

		# Find starter
		starter_pos = None
		starter_used = None
		for starter in self.starters:
			starter_pos = self.normalize(sentence).find(starter)
			if starter_pos >= 0:
				starter_used = starter
				break

		if starter_used is None:
			return
		logger.debug(f"starter `{starter_used}` found at position `{starter_pos}`")

		# Find real begining of the command
		command = next_word(sentence, starter_pos + len(starter_used))
		if command == "":
			return
		logger.debug(f"command = `{command}`")

		# Check if command matches an action
		selected_action = None
		params = None
		normalized_command = self.normalize(command)
		for action in self.actions:
			if selected_action is not None:
				break

			for starter in action["starters"]:
				logger.debug(f"checking starter `{starter}`")
				if normalized_command.startswith(starter):
					params = next_word(command, len(starter))
					selected_action = action
					break

		logger.debug(f"Parsed action {selected_action} - {params=}")
		if selected_action is None:
			return

		# Postprocess parameters
		if action["parameters-format"] == "identity":
			pass
		elif action["parameters-format"] == "lowcase-word":
			m = re.match("^([a-zA-Z]+).*$", params)
			if m is None:
				return
			params = m.group(1).lower()
		else:
			assert False, f"unknown parameters format: `{action['parameters-format']}`"

		logger.debug(f"postprocessed params `{params}`")

		# Launch command
		logger.info(f"Launcing action {selected_action['name']} - {params=}")
		threading.Thread(target=_run_action, args=(selected_action, params), daemon=True).start()

def _run_action(action, params):
	subprocess.run([action["script"], params])
