class Event:
	MESSAGE = 'MESSAGE'
	JOIN = 'JOIN'

	def __init__(self, _type, user, text):
		self._type = _type
		self.user = user
		self.text = text

	def __repr__(self):
		return '[{}] {}: {}'.format(self._type, self.user, self.text)

	def __str__(self):
		return self.__repr__()

	def message(user, text):
		return Event(Event.MESSAGE, user, text)

	def join(user):
		return Event(Event.JOIN, user, 'joined the room')