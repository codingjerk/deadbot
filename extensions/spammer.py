# Spammer extension

from extensions import base

import random
import time

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)

	def work(self):
		if random.random() < self.config['chance']:
			phrase = random.choice(self.config['phrases'])
			self.reply(phrase)

		time.sleep(1)