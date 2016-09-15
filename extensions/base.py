# Base extension

import threading

class Extension:
	def __init__(self, config):
		self.config = config
		self.terminated = False
		self.commands = {}
		self.working_thread = threading.Thread(target=self.work_base)

	def start(self, reply_command):
		self.reply_command = reply_command
		self.working_thread.start()

	def reply(self, message):
		self.reply_command(message)

	def stop(self):
		self.terminated = True
		self.wait()

	def wait(self):
		self.working_thread.join()

	def work_base(self):
		try:
			while not self.terminated:
				self.work()
		except KeyboardInterrupt as e:
			raise e

	def work(self):
		pass

	def on_join(self, user):
		pass

	def on_command(self, user, command, args):
		return False

	def on_message(self, user, text):
		return False