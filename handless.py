#!/usr/bin/env python
import actions
import listener
import logging
import pathlib
import sys
import threading
import transcripter
import utils

logger = logging.getLogger(__name__)

def transcript(my_transcript):
	my_transcript.run()

def main():
	logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s - %(message)s")

	waveforms_queue = utils.Fifo()
	sentences_queue = utils.Fifo()
	my_action_launcher = actions.ActionLauncher(["hey batman", "et batman", "eh batman"], sentences_queue)
	my_action_launcher.load_actions(pathlib.Path(__file__).parent / "actions" / "actions.yml")
	my_transcript = transcripter.Transcripter(waveforms_queue, sentences_queue)
	my_listener = listener.Listener(waveforms_queue)

	action_launcher_thread = threading.Thread(target=my_action_launcher.run, daemon=True).start()
	transcript_thread = threading.Thread(target=transcript, args=(my_transcript,), daemon=True).start()
	my_listener.run("pulse")

if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
