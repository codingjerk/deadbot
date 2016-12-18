# Mpv player extension

from extensions.players import base

import subprocess

class Player(base.Player):
	def __init__(self, config):
		super().__init__({})

		self.arguments = config['arguments']

	def open_player(self, song):
		return subprocess.Popen(
			['mpv', song] + self.arguments,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
