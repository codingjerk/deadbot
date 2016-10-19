# Uptime extension

from extensions import base

import time

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)

		self.commands = {
			'uptime': {
				'action': self.uptime_command,
				'description': 'shows time from stream start',
			},
		}

		self.start_time = time.time()

	def format_time(self, total_seconds):
		total_seconds = int(total_seconds)

		hourses = total_seconds // (60 * 60)
		rem = total_seconds - hourses * 60 * 60

		minutes = rem // 60
		rem -= minutes * 60

		seconds = rem

		return '{:02d}:{:02d}:{:02d}'.format(
			hourses, minutes, seconds
		)

	def uptime_command(self, user, command, args):
		if 'format' not in self.config:
			fmt = 'Time from stream start: {time}'
		else:
			fmt = self.config['format']

		current_time = time.time()
		uptime_seconds = current_time - self.start_time
		uptime = self.format_time(uptime_seconds)

		self.reply(fmt.format(
			time=uptime,
		))

	def on_command(self, user, command, args):
		if command not in self.commands: return False
		self.commands[command]['action'](user, command, args)

		return True