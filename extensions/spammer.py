# Spammer extension

from extensions import base

import random
import time

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)
		self.last_spam = time.time()

	def work(self):
		time.sleep(1)

		if random.random() >= self.config['chance']: return True
		if not self.recently_spammed(): return True
		self.spam()

		return True

	def spam(self):
		phrase = random.choice(self.config['phrases'])
		self.reply(phrase)

		self.last_spam = time.time()

	def recently_spammed(self):
		time_from_last_spam = time.time() - self.last_spam
		minimal_time = self.config['minimal-spam-interval']

		return time_from_last_spam <= minimal_time