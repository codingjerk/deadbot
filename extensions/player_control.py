# Player control Extension

from extensions import base

import random

class Extension(base.Extension):
	def __init__(self, config, player, scraper):
		super().__init__(config)

		self.player = player
		self.scraper = scraper
		self.dynamic_playlist = []
		self.current_song = {'title': 'unknown', 'url': 'unknown'}

		self.player.on_song_ends = self.next_song

		self.commands = {
			'play': {
				'action': self.play_command,
				'description': 'add song to playlist',
				'args': ['SONG'],
			},
			'song': {
				'action': self.song_command,
				'description': 'says current song',
			},
			'playlist': {
				'action': self.playlist_command,
				'description': 'shows playlist',
			},
		}

	def start(self, reply_command):
		super().start(reply_command)
		self.player.start(reply_command)
		self.next_song()

	def play_command(self, user, command, args):
		song = ' '.join(args)
		self.dynamic_playlist.append(song)
		self.notify_added(song)

	def song_command(self, user, command, args):
		self.reply('Current song is {title} ({url})'.format(**self.current_song))

	def playlist_command(self, user, command, args):
		dynamic = [self.current_song['title']] + self.dynamic_playlist
		fallback = self.config['fallback-playlist']

		text = '\n== Current playlist ==\n'
		text += '\n== Dynamic playlist ==\n'
		for i, song in enumerate(dynamic):
			text += '{i}. {song}\n'.format(i=i+1, song=song)

		text += '\n== Fallback playlist ==\n'
		for i, song in enumerate(fallback):
			text += '{i}. {song}\n'.format(i=i+1, song=song)

		self.reply(text)

	def pick_song(self):
		if len(self.dynamic_playlist) == 0:
			return random.choice(self.config['fallback-playlist'])

		return self.dynamic_playlist.pop(0)

	def next_song(self):
		requested_song = self.pick_song()

		if not self.scraper.can_be_scraped(requested_song):
			return self.notify_failure(requested_song)

		url, title = self.scraper.scrap(requested_song)
		if url is None or title is None:
			return self.notify_failure(requested_song)
		self.current_song = {
			'title': requested_song,
			'url': url,
		}

		try:
			self.notify_playing(url, title, requested_song)
			self.player.play(url)
		except Exception:
			# We can got this just cause notifying when bot stopping
			# It's ok
			pass

	def notify_playing(self, url, title, requested):
		if 'playing-format' not in self.config: return

		self.reply(self.config['playing-format'].format(
			url = url,
			title = title if url != title else requested,
		))

	def notify_added(self, song):
		if 'adding-format' not in self.config: return

		self.reply(self.config['adding-format'].format(song=song))

	def notify_failure(self, song):
		if 'failure-format' not in self.config: return

		self.reply(self.config['failure-format'].format(song=song))

	def on_command(self, user, command, args):
		if command not in self.commands: return False
		action = self.commands[command]['action']

		action(user, command, args)
		return True

	def wait(self):
		self.player.wait()
		super().wait()

	def stop(self):
		self.player.stop()
		super().stop()