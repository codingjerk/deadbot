# Variables extension

from extensions import base

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)
		self.variables = config['vars']
		self.commands = {
			'set': {
				'action': self.set_command,
				'favored-only': True,
				'description': 'sets variable. Only for favored users',
			},
			'unset': {
				'action': self.unset_command,
				'favored-only': True,
				'description': 'removes variable. Only for favored users',
			},
			'get': {
				'action': self.get_command,
				'description': 'gets variable',
			},
		}

		if self.need_to_append_commands():
			for name in self.variables:
				self.append_as_command(name)

	def need_to_append_commands(self):
		if 'allow-to-use-variables-as-commands' not in self.config:
			return False

		return self.config['allow-to-use-variables-as-commands']

	def append_as_command(self, name):
			self.commands[name] = {
				'action': self.get_by_command,
				'description': 'shows {}'.format(name),
			}

	def set_command(self, user, command, args):
		[name, *args] = args
		value = ' '.join(args)
		self.variables[name] = value
		
		if self.need_to_append_commands():
			self.append_as_command(name)

		if 'set-format' not in self.config: return

		self.reply(self.config['set-format'].format(
			name=name,
			value=value,
		))

	def unset_command(self, user, command, args):
		[name, *_] = args
		if name not in self.variables:
			self.notify_unknown(name)

		del self.variables[name]
		if self.need_to_append_commands():
			del self.commands[name]

		if 'unset-format' not in self.config: return

		self.reply(self.config['unset-format'].format(
			name=name,
		))

	def notify_unknown(self, name):
		if 'unknown-format' not in self.config: return

		self.reply(self.config['unknown-format'].format(
			name=name
		))

	def show_variable(self, name):
		if name not in self.variables:
			return self.notify_unknown(name)

		if 'show-format' not in self.config: return

		self.reply(self.config['show-format'].format(
			name=name,
			value=self.variables[name],
		))

	def get_by_command(self, user, command, args):
		self.show_variable(command)

	def get_command(self, user, command, args):
		name = ' '.join(args)
		self.show_variable(name)

	def on_command(self, user, command, args):
		if command not in self.commands: return False
		self.commands[command]['action'](user, command, args)

		return True