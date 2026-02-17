import threading
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
		self.condition = threading.Condition()

	def push(self, item):
		self._debug("pushing item")

		with self.condition:
			if len(self.queue) >= self.queue_size:
				self._warning(f"queue {self.name}: queue full, lost item")
				return

			self.queue.append(item)
			self.condition.notify_all()

	def pop(self):
		self._debug("poping item")
		with self.condition:
			while len(self.queue) == 0:
				self.condition.wait()

			self._debug("POP!")
			item = self.queue[0]
			self.queue = self.queue[1:]
		return item

	def _debug(self, m):
		logger.debug(f"queue {self.name}: {m}")

	def _warning(self, m):
		logger.warning(f"queue {self.name}: {m}")
