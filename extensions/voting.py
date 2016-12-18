# Voting extension

from extensions import base

import csv, io

class Voting:
	def __init__(self, title, end, variants):
		self.title = title
		self.end = end
		self.variants = variants
		self.votes = [0] * len(self.variants)
		self.voted_users = {}

	def vote(self, user, variant):
		if user in self.voted_users:
			old_variant = self.voted_users[user]
			self.votes[old_variant - 1] -= 1

		self.votes[variant - 1] += 1
		self.voted_users[user] = variant

	def to_string(self):
		result = '\n[Voting: {}]\n'.format(self.title)
		for i, variant in enumerate(self.variants):
			result += '{}. {} ({})\n'.format(i + 1, variant, self.votes[i])

		return result

	def ended(self):
		return False # TODO: check end condition

	def available_variants(self):
		return range(1, len(self.variants) + 1)

class NullVoting(Voting):
	def __init__(self):
		pass

	def vote(self, user, variant):
		pass

	def ended(self):
		return True

	def available_variants(self):
		return []

class Extension(base.Extension):
	def __init__(self, config):
		super().__init__(config)

		self.commands = {
			'start_voting': {
				'action': self.start_voting_command,
				'favored-only': True,
				'description': 'starts voting',
				'args': ['TITLE', 'END CONDITION', 'VOTING VARIANTS'],
			},
			'end_voting': {
				'action': self.end_voting_command,
				'favored-only': True,
				'description': 'ends voting',
			},
			'vote': {
				'action': self.vote_command,
				'description': 'votes in current voting',
				'args': ['VARIANT'],
			},
		}

		self.current_voting = NullVoting()

	def show_voting(self):
		self.reply(self.current_voting.to_string())

	def notify_ended(self):
		# TODO: config format
		# TODO: show voting result
		self.reply("Voting was ended")

	def notify_bad_variant(self):
		# TODO: config format
		self.reply("Bad voting variant")

	def extract_args(self, args):
		str_args = io.StringIO(' '.join(args))
		new_args = list(csv.reader(str_args, delimiter=' '))[0]

		return new_args

	def create_voting(self, title, end, variants):
		# TODO: check end condition
		return Voting(title, end, variants)

	def start_voting_command(self, user, command, args):
		[title, end, *variants] = self.extract_args(args)
		self.current_voting = self.create_voting(title, end, variants)
		self.show_voting()

	def end_voting_command(self, user, command, args):
		self.current_voting = NullVoting()
		self.notify_ended()

	def vote_command(self, user, command, args):
		if self.current_voting.ended():
			return self.notify_ended()

		try:
			variant = int(args[0])
		except (ValueError, IndexError):
			return self.notify_bad_variant()

		if variant not in self.current_voting.available_variants():
			return self.notify_bad_variant()

		self.current_voting.vote(user, variant)
		self.show_voting()

	def on_command(self, user, command, args):
		if command not in self.commands: return False
		self.commands[command]['action'](user, command, args)

		return True
