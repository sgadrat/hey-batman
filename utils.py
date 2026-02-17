import time
import logging

logger = logging.getLogger(__name__)

class Fifo:
	"""
	Thread-safe fifo
	"""
	def __init__(self, queue_size = 10, name = "queue"):
		self.queue_size = queue_size
		self.name = "queue"
		self.queue = []

	def push(self, item):
		self._debug("pushed item")
		#TODO lock
		if len(self.queue) >= self.queue_size:
			self._warning(f"queue {self.name}: queue full, lost item")
			return

		self.queue.append(item)
		#TODO condition notify

	def pop(self):
		#TODO lock
		#TODO condition wait
		while len(self.queue) == 0:
			self._debug("pop wait")
			time.sleep(0.5)

		self._debug("POP!")
		item = self.queue[0]
		self.queue = self.queue[1:]
		return item

	def _debug(self, m):
		logger.debug(f"queue {self.name}: {m}")

	def _warning(self, m):
		logger.warning(f"queue {self.name}: {m}")
