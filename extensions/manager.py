import time

class Manager:
	def __init__(self, config, engine, extensions, extension_names):
		self.config = config
		self.engine = engine
		self.extensions = extensions
		self.extension_names = extension_names

		if 'greeting' in self.config: self.reply(self.config['greeting'])

		# Small delay needed to skip initial bunch on events
		time.sleep(0.5)

		[e.start(self.reply) for e in self.extensions]
		engine.subscribe('on-join', self.on_join)
		engine.subscribe('on-message', self.on_message_event)

	def reply(self, message):
		return self.engine.send(self.config['message-format'].format(text=message))

	def on_join(self, event):
		[e.on_join(event.user) for e in self.extensions]

	def on_message_event(self, event):
		if event.text.startswith(self.config['command-prefix']):
			return self.on_command(event)
		else:
			return self.on_message(event)

	def on_command(self, event):
		[command, *args] = event.text[len(self.config['command-prefix']):].split(' ')

		if command == 'help':
			return self.help_command(args, event)

		results = [e.on_command(event.user, command, args) for e in self.extensions]
		if not any(results):
			self.reply('I don\' know that command')

	def on_message(self, event):
		[e.on_message(event.user, event.text) for e in self.extensions]

	def get_command_args_help(self, command):
		if 'args' not in command: return ''
		return ', '.join('<%s>' % arg for arg in command['args'])

	def get_command_description(self, command):
		if 'description' not in command: return 'unknown description'
		return command['description']

	def get_command_help(self, name, command):
		return '{prefix}{name} {args} - {desc}\n'.format(
			prefix=self.config['command-prefix'],
			name=name,
			args=self.get_command_args_help(command),
			desc=self.get_command_description(command),
		)

	def get_extension_help(self, name, extension):
		if len(extension.commands) == 0: return ''

		result = '\n== [{}] extension ==\n'.format(name.title())
		for name, command in extension.commands.items():
			result += self.get_command_help(name, command)

		return result

	def help_command(self, args, event):
		result = '\n== Help ==\n'

		result += self.get_command_help('help', {
			'description': 'shows this help',
		})

		for name, extension in zip(self.extension_names, self.extensions):
			result += self.get_extension_help(name, extension)

		self.reply(result)

	def wait(self):
		try:
			self.engine.wait()

			for extension in self.extensions:
				extension.wait()
		except KeyboardInterrupt as e:
			pass
		finally:
			self.stop()

	def stop(self):
		if 'parting' in self.config: self.reply(self.config['parting'])
		self.engine.stop()

		for extension in self.extensions:
			extension.stop()