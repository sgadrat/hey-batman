Description
===========

Vocal command launcher. Talk to your PC and it starts scripts.

This is not an assistant, it does not aswers you, just a hand-free way of starting your common tasks.

Usage
=====

python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
./handless.py

The talk, you terminal can be in the background and you can be doing other things. Try to say "Hey Batman! command Firefox."

Configuration is in config.yml and possible actions are in the actions/ directory. Default config is minimalistic example, optimized for a French speaker in a quiet environment.

Under the hood
==============

The application listens continuously to the mic. When it detects non-silent segments, it processes it with Whisper to get a textual representation then iterprets it mechanically (no LLM at this stage.)

- Get non-silent segments from the mic
- Convert it to text (using Whisper)
- Convert text to action (in simple, dumb, good old logic, based on searching actions' names in the sentence)
- Launch the script referenced by the action (a .sh you wrote that suits your need)

Everything happens locally. Whisper model is run on your computer, it is speedy enough for most computers.
