# Mpv player extension

from extensions.players import base

import subprocess

class Player(base.Player):
	def __init__(self):
		super().__init__({})

	def open_player(self, song):
		return subprocess.Popen(
			['mpv', song, '--vo', 'null'],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)