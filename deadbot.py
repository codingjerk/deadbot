#!/usr/bin/env python

import sys
import time
import io
import subprocess
import re
import random

from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException

from lxml import etree

class AuthMethod:
	# TODO: add and allow other auth methods
	GOOGLE = 'GOOGLE'
	DIRECT = 'DIRECT'

class Event:
	MESSAGE = 'MESSAGE'
	JOIN = 'JOIN'

	def __init__(self, type, time, username, text):
		self.type     = type
		self.time     = time
		self.username = username
		self.text     = text

	def message(time, username, text):
		return Event(Event.MESSAGE, time, username, text)

	def join(username):
		return Event(Event.JOIN, None, username, 'joined the room')

	def __eq__(self, other):
		if self.type != other.type:
			return False

		if self.time != other.time:
			return False

		if self.username != other.username:
			return False

		if self.text != other.text:
			return False

		return True

	def __str__(self):
		return '{}: {} -- {}'.format(
			self.type, self.username, self.text
		)

	def __repr__(self):
		return self.__str__()

class Player:
	def __init__(self, pool):
		self.playlist = []
		# TODO: load fallback songs from config file
		self.fallback_songs = [
			'https://www.youtube.com/watch?v=O6NvsM49N6w',
			'https://www.youtube.com/watch?v=7ZFWDaRy9Z4',
			'https://www.youtube.com/watch?v=n8X9_MgEdCg',
			'https://www.youtube.com/watch?v=B7xai5u_tnk',
			'https://www.youtube.com/watch?v=3fxq7kqyWO8',
			'https://www.youtube.com/watch?v=ih2xubMaZWI',
			'https://www.youtube.com/watch?v=qn-X5A0gbMA',
			'https://www.youtube.com/watch?v=2ggzxInyzVE',
			'https://www.youtube.com/watch?v=psuRGfAaju4',
			'https://www.youtube.com/watch?v=J2X5mJ3HDYE',
			'https://www.youtube.com/watch?v=UbQgXeY_zi4',
			'https://www.youtube.com/watch?v=O5ZN3_svgs0',
			'https://www.youtube.com/watch?v=-Tdu4uKSZ3M',
		]

		self.mpv = None
		self.pool = pool

	def add(self, song):
		self.playlist.append(song)

		if self.current in self.fallback_songs:
			self.next_song()
		else:
			self.pool.say('Adding {} to playlist'.format(song))

	def is_url(self, song):
		return song[:4] == 'http'

	def next_song(self):
		if len(self.playlist) > 0:
			song = self.playlist.pop()
		else:
			song = random.choice(self.fallback_songs)

		self.play(song)

	def get_url_by_song_name(self, song):
		process = subprocess.Popen(['GoogleScraper', '-m', 'http', '-q', song], stdout=subprocess.PIPE)
		process.wait()
		output = process.communicate()[0].decode().split('\n')

		print(output)

		youtube_links = [link for link in output
			if "link':" in link and "https://www.youtube.com/watch?v=" in link
		]

		print(youtube_links)

		if len(youtube_links) == 0:
			return None

		extracted_links = re.findall('https://www.youtube.com/watch[^\']+', youtube_links[0])

		print(extracted_links)

		if len(extracted_links) == 0:
			return None

		return extracted_links[0]

	def play(self, song):
		self.current = song
		self.pool.say('Playing {}'.format(song))

		if self.mpv is not None:
			self.mpv.kill()

		if self.is_url(song):
			url = song
		else:
			url = self.get_url_by_song_name(song)

		if url is None:
			self.pool.say('Sorry, i cant play song {}'.format(song))
			return

		self.mpv = subprocess.Popen(
			['mpv', url, '--vo', 'null'],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)

	def ping(self):
		if self.mpv is not None:
			if self.mpv.poll() is None: return

		self.next_song()

class EventPool:
	def __init__(self, driver, auth_data):
		self.driver = driver
		self.player = Player(self)
		self.events = []
		self.skip_counter = 0
		self.auth_data = auth_data

		self.project = 'Unknown'
		self.github_url = 'Unknown'

		self.max_skip_counter = 4

		self.commands = {
			'!hi': (self.hi, 'say hi to deadbot'),
			'!help': (self.help, 'shows this help'),
			'!say': (self.say_command, 'ask bot to say something'),
			'!play': (self.play, 'add song to playlist (you can use youtube links or song names)'),
			'!current': (self.current_command, 'says current song'),
			'!song': (self.current_command, 'says current song'),
			'!playlist': (self.playlist_command, 'show current playlist queue'),
			'!skip': (self.skip_command, 'vote for skipping current song'),
			'!noskip': (self.noskip_command, 'vote for no skipping current song'),
			'!propose': (self.propose_command, 'propose project to write for streamer'),
			'!project': (self.project_command, 'shows (or sets with admin rights) current project name'),
			'!github': (self.github_command, 'shows (or sets with admin rights) current project github url'),
		}

		# TODO: get greets from config
		self.greets = [
			'Oh my god! It\'s {}!',
			'Hi {}, how r u?',
			'New viewer here: {}. Regards.',
			'Hi {}.',
			'Ohoho! Hi {}.',
			'I was waiting for u, {}.',
			'Greetings from the soulless machine, {}!',
		]

		self.phrases = [
			'Write !help to know that I can do.',
			'Just reminder that I\'ve work as a chat bot here.'
			'Hi mates. I\'m a Deadbot :D',
		]

	def add(self, events, process=True):
		for event in events:
			if event not in self.events:
				if process:
					self.process(event)
				self.events.append(event)

	def process(self, event):
		print(event)

		text = event.text

		if event.type == Event.JOIN:
			greet = random.choice(self.greets)
			self.say(greet.format(event.username))
			return

		if len(text) <= 1: return
		if text[0] != '!': return

		[command, *args] = text.split(' ')

		if command in self.commands:
			self.commands[command][0](event, args)
		else:
			self.unknown_command(command)

	def hi(self, event, args):
		self.say('Hi, {}'.format(event.username))

	def help(self, event, args):
		items = sorted(self.commands.items())
		for (command_name, (_, command_description)) in items:
			self.say('{} -- {}'.format(command_name, command_description))

	def say_command(self, event, args):
		self.say(' '.join(args))

	def current_command(self, event, args):
		self.say('Current song is {}'.format(self.player.current))

	def playlist_command(self, event, args):
		self.say('Current playlist:')
		self.say('  - {} (CURRENT)'.format(self.player.current))

		for song in self.player.playlist:
			self.say('  - {}'.format(song))

	def skip_command(self, event, args):
		self.skip_counter += 1
		self.say('Votes for skipping current song: {}/{}'.format(self.skip_counter, self.max_skip_counter))

		if self.skip_counter >= self.max_skip_counter:
			self.say('Too much votes! Skipping!')
			self.skip_counter = 0
			self.player.mpv.kill()

	def noskip_command(self, event, args):
		self.skip_counter -= 1
		self.skip_counter = max(0, self.skip_counter - 1)

		self.say('Votes for skipping current song: {}/{}'.format(self.skip_counter, self.max_skip_counter))

	def propose_command(self, event, args):
		self.say('User {} propose project for streamer: {}'.format(
			event.username,
			' '.join(args),
		))

	def project_command(self, event, args):
		if len(args) == 0:
			self.say('Current project: {}'.format(self.project))
		elif event.username == self.auth_data['channel']:
			self.project = self.project = ' '.join(args)

	def github_command(self, event, args):
		if len(args) == 0:
			self.say('Github url: {}'.format(self.github_url))
		elif event.username == self.auth_data['channel']:
			self.github_url = self.github_url = ' '.join(args)

	def unknown_command(self, command):
		self.say('Unknown command "{}". Write "!help" for list of available commands.'.format(command))

	def play(self, event, args):
		song = ' '.join(args).strip()
		self.player.add(song)

	def say(self, message):
		textarea = self.driver.find_element_by_id('message-textarea')
		textarea.send_keys('[DeadBot] {}\n'.format(message))

	def ping(self):
		self.player.ping()

		# With a little chance write something to chat
		if random.random() < 0.001:
			phrase = random.choice(self.phrases)
			self.say(phrase)

	@property
	def size(self):
		return len(self.events)

def parse_auth_data(args):
	# TODO: temporary, use config
	return {
		'username': open('username.secret').read(),
		'password': open('password.secret').read(),
		'channel': 'd3adc0d3',
	}

def wait_element(f):
		while True:
			try:
				return f()
			except (NoSuchElementException, ElementNotVisibleException):
				time.sleep(0.05)

# TODO: allow to select from config
def connect_to_livecoding(method, auth_data):
	login_url = 'https://www.livecoding.tv/accounts/login/'

	driver = webdriver.Chrome()
	driver.get(login_url)

	if method == AuthMethod.GOOGLE:
		google_button = driver.find_element_by_class_name('google')
		google_button.click()

		if 'username' in auth_data:
			def userinput():
				username_input = driver.find_element_by_id('Email')
				username_input.send_keys(auth_data['username'] + '\n')

			wait_element(userinput)

			if 'password' in auth_data:
				def password():
					password_input = driver.find_element_by_id('Passwd')
					password_input.send_keys(auth_data['password'] + '\n')

				wait_element(password)

		while driver.current_url != 'https://www.livecoding.tv/categories/#':
			time.sleep(0.05)

	return driver

def go_to_chat(driver, auth_data):
	chat_url = 'https://www.livecoding.tv/{}/chat'.format(auth_data['channel'])
	driver.get(chat_url)

def parse_event(event_html):
	parser = etree.HTMLParser()
	event_node = etree.parse(io.StringIO(event_html), parser).getroot()[0][0]

	if 'message-info' in event_node.attrib['class']:
		username= event_node.text.split(' ')[0]

		return Event.join(username)
	else:
		time = event_node[0][0].text
		username = event_node[0][0].tail

		text = event_node[0].tail if event_node[0].tail is not None else ''
		for child in event_node[1:]:
			child_text = child.text if child.text is not None else ''
			child_tail = child.tail if child.tail is not None else ''
			text += ' ' + child_text + child_tail

		return Event.message(time, username, text)

def parse_events(driver):
	events = [parse_event(e.get_attribute('outerHTML'))
		for e in driver.find_elements_by_class_name('message')
	]

	return events

def track_events(driver, auth_data):
	while True:
		events = parse_events(driver)
		if len(events) > 0:
			event_pool = EventPool(driver, auth_data)
			event_pool.add(events, False)
			break

		time.sleep(0.3)

	event_pool.say('Hi chat. I\'m alive!')

	try:
		while True:
			try:
				events = parse_events(driver)
			except StaleElementReferenceException:
				# HACK
				# I dont know why, but sometimes selenium got this exception
				# Its cause tree changes while makes query, i guess
				continue

			event_pool.add(events, True)
			event_pool.ping()

			time.sleep(0.1)
	except KeyboardInterrupt:
		event_pool.say('Oh, I need to sleep for a while')

def main(args):
	auth_data = parse_auth_data(args)
	driver = connect_to_livecoding(AuthMethod.GOOGLE, auth_data)
	go_to_chat(driver, auth_data)
	track_events(driver, auth_data)

if __name__ == '__main__':
	main(sys.argv[1:])