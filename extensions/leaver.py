# Leaver extension

from extensions import base

import random

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)

	def on_leave(self, user):
		greet = random.choice(self.config['messages'])
		self.reply(greet.format(user=user))
