# Base player extension

from extensions import base

import time

class Player(base.Extension):
	def __init__(self, *args, **kwargs):
		self.proc = None
		self.current_song = None
		self.on_song_ends = None

		super().__init__(*args, **kwargs)

	def work(self):
		song = self.current_song

		if song is None:
			time.sleep(0.5)
			return

		self.proc = self.open_player(song)
		try:
			self.proc.wait()
		except KeyboardInterrupt as e:
			self.proc.kill()
			raise e

		if self.on_song_ends is not None:
			self.on_song_ends()

	def play(self, song):
		self.current_song = song
		if self.proc is not None: self.proc.kill()

	def stop(self):
		self.terminated = True
		if self.proc is not None: self.proc.kill()
		self.wait()

	def wait(self):
		if self.proc is not None: self.proc.wait()