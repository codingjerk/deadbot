# Commands extension

from extensions import base

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)
		self.commands = self.config

	def on_command(self, user, command, args):
		if command not in self.commands: return False

		answer = self.commands[command]['answer'].format(
			user=user,
			args=' '.join(args),
		)
		self.reply(answer)

		return True