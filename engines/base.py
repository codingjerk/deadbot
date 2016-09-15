# Base engine

import events

import threading

class Engine:
	def __init__(self, config):
		self.config = config
		self.terminated = False
		self.working_thread = threading.Thread(target=self.work_base)
		self.on_join_listeners = []
		self.on_message_listeners = []

		self.connect()
		self.working_thread.start()

	def send_event(self, event):
		if not self.event_can_be_processed(event): return

		if event._type == events.Event.JOIN:
			return self.on_join(event)
		elif event._type == events.Event.MESSAGE:
			return self.on_message(event)
		else:
			print('Unknown event type:', event)

	def subscribe(self, event, listener):
		if event == 'on-join':
			self.on_join_listeners.append(listener)
		elif event == 'on-message':
			self.on_message_listeners.append(listener)

	def on_join(self, event):
		for listener in self.on_join_listeners:
			listener(event)

	def on_message(self, event):
		for listener in self.on_message_listeners:
			listener(event)

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
		if self.config['ignore-own-messages']:
			if event.user == self.config['bot-name']: return False

		return True

	def stop(self):
		self.terminated = True
		self.wait()

	def wait(self):
		self.working_thread.join()

	def send(self, message):
		pass