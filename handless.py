#!/usr/bin/env python
import actions
import listener
import logging
import pathlib
import sys
import threading
import transcripter
import utils
import yaml

logger = logging.getLogger(__name__)

def transcript(my_transcript):
	my_transcript.run()

def main():
	logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s %(levelname)s - %(message)s")

	# Load configuration file
	config_basedir = pathlib.Path(__file__).parent
	config_path = config_basedir / "config.yml"
	with open(config_path, "r") as config_file:
		config = yaml.load(config_file, Loader=yaml.CLoader)

	config["actions"] = pathlib.Path(config["actions"])
	if not config["actions"].is_absolute():
		config["actions"] = str((config_basedir / config["actions"]).absolute())

	# Create application's components
	waveforms_queue = utils.Fifo()
	sentences_queue = utils.Fifo()
	my_action_launcher = actions.ActionLauncher(config["starters"], sentences_queue)
	my_action_launcher.load_actions(pathlib.Path(__file__).parent / "actions" / "actions.yml")
	my_transcript = transcripter.Transcripter(waveforms_queue, sentences_queue)
	my_listener = listener.Listener(
		waveforms_queue,
		config.get("listener", {}).get("silence_threshold", 400),
		config.get("listener", {}).get("segment_duration", 0.25),
		config.get("listener", {}).get("nb_silence_to_flush", 2),
	)

	# Start components
	action_launcher_thread = threading.Thread(target=my_action_launcher.run, daemon=True).start()
	transcript_thread = threading.Thread(target=transcript, args=(my_transcript,), daemon=True).start()
	my_listener.run("pulse")

if __name__ == "__main__":
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
