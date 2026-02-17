#!/usr/bin/env python
import listener
import logging
import sys
import threading
import transcripter
import utils

logger = logging.getLogger(__name__)

def transcript(my_transcript):
	my_transcript.run()

def main():
	logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s - %(message)s")

	my_fifo = utils.Fifo()
	my_transcript = transcripter.Transcripter(my_fifo)
	my_listener = listener.Listener(my_fifo)

	transcript_thread = threading.Thread(target=transcript, args=(my_transcript,), daemon=True).start()
	my_listener.run("pulse")

if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
