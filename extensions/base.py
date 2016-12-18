# Base extension

import threading

class Extension:
	def __init__(self, config):
		self.config = config
		self.terminated = False
		self.commands = {}
		self.working_thread = threading.Thread(target=self.work_base)

	def start(self, reply_commands):
		self.reply_command, self.reply_code_command = reply_commands
		self.working_thread.start()

	def reply(self, message):
		self.reply_command(message)

	def reply_code(self, message):
		self.reply_code_command(message)

	def stop(self):
		self.terminated = True
		self.wait()

	def wait(self):
		self.working_thread.join()

	def work_base(self):
		try:
			while not self.terminated and self.work(): pass
		except KeyboardInterrupt as e:
			raise e

	def work(self):
		return False

	def on_join(self, user):
		pass

	def on_command(self, user, command, args):
		return False

	def on_message(self, user, text):
		return False
