# Base engine

import threading

# TODO: engine looks like extension, maybe make base.Extension base class for engine and use it like other extensions?
class Engine:
	def __init__(self, config):
		self.config = config
		self.terminated = False
		self.on_event = None
		self.working_thread = threading.Thread(target=self.work_base)

		self.start()
		self.working_thread.start()

	def work_base(self):
		try:
			while not self.terminated:
				self.work()
		except KeyboardInterrupt:
			pass

	def work(self):
		pass

	def event_can_be_processed(self, event):
		if event is None: return False
		if self.on_event is None: return False
		if self.config['ignore-own-messages']:
			if event.user == self.config['bot-name']: return False

		return True

	def stop(self):
		self.terminated = True
		self.wait()

	def wait(self):
		self.working_thread.join()