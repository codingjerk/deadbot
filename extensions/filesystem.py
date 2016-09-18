# Filesystem Extension

from extensions import base

import os

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)

		self.root = os.path.realpath(
			os.path.expanduser(
				self.config['root']
			)
		)

		if not os.path.exists(self.root):
			os.mkdir(self.root)

		self.pwds = {}

		self.commands = {
			'ls': {
				'action': self.ls_command,
				'description': 'shows content of current directory',
			},
			'pwd': {
				'action': self.pwd_command,
				'description': 'shows current directory',
			},
			'cat': {
				'action': self.cat_command,
				'description': 'shows content of given file',
				'args': ['FILE'],
			},
			'cd': {
				'action': self.cd_command,
				'description': 'changes current directory',
				'args': ['DIRECTORY'],
			},

			# TODO: touch, echo >, rm, git, grep, shell-like parser
		}

	def get_user_pwd(self, user):
		if user not in self.pwds: self.pwds[user] = self.root

		return self.pwds[user]

	def show_path(self, path):
		return os.path.relpath(path, start=self.root)

	def path_in_root(self, path):
		path = os.path.realpath(path)
		return path.startswith(self.root)

	def ls_command(self, user, command, args):
		# TODO: arguments
		# TODO: config (format)

		dir = self.get_user_pwd(user)
		result = '/code'
		
		items = os.listdir(dir)
		if len(items) == 0:
			result += '<Empty>'
		else:
			result += '\n'.join(
				'* {}'.format(item)
				for item in items
			)

		self.reply(result)

	def pwd_command(self, user, command, args):
		# TODO: arguments
		dir = self.get_user_pwd(user)
		result = '/code'
		result += self.show_path(dir)

		self.reply(result)

	def cat_command(self, user, command, args):
		# TODO: arguments
		# TODO: ~
		dir = self.get_user_pwd(user)
		file = ' '.join(args)
		file_path = os.path.join(dir, file)

		if not self.path_in_root(file_path):
			return self.reply('You do not have access to this file')

		if not os.path.exists(file_path):
			return self.reply('File does not exist')

		if not os.path.isfile(file_path):
			return self.reply('This is not a file')

		# TODO: use code for code files
		# TODO: better use gists or pastebin for big files
		# TODO: use async io for perfomace
		# TODO: use self.reply_code, cause code is only supported by livecoding.tv
		result = '/code'

		result += open(file_path).read()

		self.reply(result)

	def cd_command(self, user, command, args):
		dir = self.get_user_pwd(user)
		subdir = ' '.join(args)
		newdir = os.path.realpath(os.path.join(dir, subdir))

		if not self.path_in_root(newdir):
			return self.reply('You do not have access to this directory')

		if not os.path.exists(newdir):
			return self.reply('Directory does not exist')

		if not os.path.isdir(newdir):
			return self.reply('This is not a directory')

		self.pwds[user] = newdir

	def on_command(self, user, command, args):
		if command not in self.commands: return False
		action = self.commands[command]['action']

		action(user, command, args)
		return True