# Livecoding.tv engine

from engines import base
import events

import websocket
from lxml import etree
from xml.sax import saxutils

class Engine(base.Engine):
	def __init__(self, config):
		self.setup_key(config)
		super().__init__(config)

	def setup_key(self, config):
		if 'bot-key' in config: return
		if 'bot-key-file' not in config:
			raise BadConfigException('No key in config')

		key = open(config['bot-key-file']).read()
		config['bot-key'] = key.strip()

	def work(self):
		try:
			response = self.connection.recv()
		except websocket._exceptions.WebSocketConnectionClosedException:
			return print('Connection was closed')

		event = self.parse_response(response)
		self.send_event(event)

	def stop(self):
		self.connection.close(timeout=0)
		super().stop()

	def connect(self):
		# TODO: replace EZyDJJ42-popout
		# TODO: write common method for sending (raw) messages
		# TODO: move this to separate file
		# TODO: check for success for some messages

		# TODO: ping with <iq type='get' to='livecoding.tv' xmlns='jabber:client' id='16:sendIQ'><ping xmlns='urn:xmpp:ping'/></iq>
		# <iq from='livecoding.tv' to='d3adc0d3@livecoding.tv/web-d3adc0d3-gIsqUZ6F-popout' type='error' id='16:sendIQ'><ping xmlns='urn:xmpp:ping'/><error code='501' type='cancel'><feature-not-implemented xmlns='urn:ietf:params:xml:ns:xmpp-stanzas'/></error></iq>

		connection_messages = [
			(2, "<stream:stream to='livecoding.tv' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"),
			(1, "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{key}</auth>"),
			(2, "<stream:stream to='livecoding.tv' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"),
			(1, "<iq type='set' id='_bind_auth_2' xmlns='jabber:client'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>web-{channel}-EZyDJJ42-popout</resource></bind></iq>"),
			(1, "<iq type='set' id='_session_auth_2' xmlns='jabber:client'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>"),
			(0, "<presence id='pres:1' xmlns='jabber:client'><priority>1</priority><c xmlns='http://jabber.org/protocol/caps' hash='sha-1' node='https://candy-chat.github.io/candy/' ver='kR9jljQwQFoklIvoOmy/GAli0gA='/></presence>"),
			(0, "<iq type='get' from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv' xmlns='jabber:client' id='2:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info'/></iq>"),
			(0, "<presence to='{channel}@chat.livecoding.tv/{name}' id='pres:3' xmlns='jabber:client'><x xmlns='http://jabber.org/protocol/muc'/><c xmlns='http://jabber.org/protocol/caps' hash='sha-1' node='https://candy-chat.github.io/candy/' ver='kR9jljQwQFoklIvoOmy/GAli0gA='/></presence>"),
			(2, "<iq type='get' from='{name}@livecoding.tv' xmlns='jabber:client' id='4:sendIQ'><query xmlns='jabber:iq:privacy'><list name='ignore'/></query></iq>"),
			(1, "<iq type='set' from='{name}@livecoding.tv' xmlns='jabber:client' id='6:sendIQ'><query xmlns='jabber:iq:privacy'><list name='ignore'><item action='allow' order='0'/></list></query></iq>"),
			(1, "<iq type='set' from='{name}@livecoding.tv' xmlns='jabber:client' id='7:sendIQ'><query xmlns='jabber:iq:privacy'><active name='ignore'/></query></iq>"),

			(2, "<iq from='{name}@livecoding.tv' to='{channel}@livecoding.tv/web-{channel}-EZyDJJ42-popout' type='get' xmlns='jabber:client' id='7:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(0, "<iq type='set' from='{name}@livecoding.tv' xmlns='jabber:client' id='8:sendIQ'><query xmlns='jabber:iq:privacy'><list name='ignore'><item action='allow' order='0'/></list></query></iq>"),
			(2, "<iq type='set' from='{name}@livecoding.tv' xmlns='jabber:client' id='9:sendIQ'><query xmlns='jabber:iq:privacy'><active name='ignore'/></query></iq>"),
			(1, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/kndr' type='get' xmlns='jabber:client' id='10:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(1, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/ney123456789' type='get' xmlns='jabber:client' id='11:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(1, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/drmjg' type='get' xmlns='jabber:client' id='12:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(1, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/rex2' type='get' xmlns='jabber:client' id='13:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(1, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/marianyc' type='get' xmlns='jabber:client' id='14:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
			(0, "<iq from='{name}@livecoding.tv' to='{channel}@chat.livecoding.tv/{name}' type='get' xmlns='jabber:client' id='15:sendIQ'><query xmlns='http://jabber.org/protocol/disco#info' node='https://candy-chat.github.io/candy/#kR9jljQwQFoklIvoOmy/GAli0gA='/></iq>"),
		]

		self.connection = websocket.create_connection("wss://ws.www.livecoding.tv/chat/websocket")

		for i, (to_skip, message) in enumerate(connection_messages):
			self.connection.send(message.format(
				key=self.config['bot-key'],
				name=self.config['bot-name'],
				channel=self.config['channel'],
			))
			[self.connection.recv() for _ in range(to_skip)]

	# TODO: try to get "follow" events
	def parse_response(self, response):
		try:
			root = etree.fromstring(response)
		except etree.XMLSyntaxError:
			print('Bad XML:', response)
			return None

		if self.is_message(root):
			return self.process_message(root)
		elif self.is_ignored_event(root):
			pass
		elif self.is_join(root):
			return self.process_join(root)
		else:
			print('Unknown message: ', response)

	def is_message(self, root):
		if root.tag != 'message': return False
		if 'from' not in root.attrib: return False
		if '/' not in root.attrib['from']: return False
		if root.find('body') is None: return False

		return True

	def is_ignored_event(self, root):
		# TODO: check why we get this
		def is_iq_error():
			if root.tag != 'iq': return False
			if 'type' not in root.attrib: return False
			if root.attrib['type'] != 'error': return False

			error_node = root.find('error')
			if error_node is None: return False

			text_node = error_node.find('{urn:ietf:params:xml:ns:xmpp-stanzas}text')
			if text_node is not None:
				if text_node.text == 'Queries to the conference members are not allowed in this room': return True

			feature_node = error_node.find('{urn:ietf:params:xml:ns:xmpp-stanzas}feature-not-implemented')
			if feature_node is None: return False

			return True

		# TODO: check why we get this
		def is_iq_unavailable():
			if root.tag != 'iq': return False
			if 'type' not in root.attrib: return False
			if root.attrib['type'] != 'error': return False

			error_node = root.find('error')
			if error_node is None: return False

			return error_node.find(
				'{urn:ietf:params:xml:ns:xmpp-stanzas}service-unavailable'
			) is not None

		# TODO: check why we get this
		def is_iq_get():
			if root.tag != 'iq': return False
			if 'type' not in root.attrib: return False
			if root.attrib['type'] != 'get': return False
			if 'id' not in root.attrib: return False
			if ':sendIQ' not in root.attrib['id']: return False

			return True

		# TODO: check why we get this
		def is_presence_unavailable():
			if root.tag != 'presence': return False
			if 'type' not in root.attrib: return False
			if root.attrib['type'] != 'unavailable': return False

			return True

		# TODO: check why we get this
		def is_presence_caps():
			if root.tag != 'presence': return False
			if 'id' not in root.attrib: return False
			if root.attrib['id'] != 'pres:1': return False

			c_node = root.find('{http://jabber.org/protocol/caps}c')
			if c_node is None: return False

			return True

		return any([
			is_iq_error(),
			is_iq_get(),
			is_presence_unavailable(),
			is_presence_caps(),
			is_iq_unavailable(),
		])

	def is_join(self, root):
			if root.tag != 'presence': return False

			jabber_x_node = root.find('{http://jabber.org/protocol/muc#user}x')
			if jabber_x_node is None: return False
			if 'from' not in root.attrib: return False
			if '/' not in root.attrib['from']: return False

			return True

	def process_message(self, root):
		user = root.attrib['from'].split('/')[-1]
		text = root.find('body').text or ''

		return events.Event.message(user, text)

	def process_join(self, root):
		jid = root.attrib['from'].split('/')[-1]

		# TODO: get user role from root/x/item@role and root/x/item@affiliation
		user = jid.split('@')[0]

		return events.Event.join(user)

	def send(self, message):
		message = saxutils.escape(message)
		send_command = "<message to='{channel}@chat.livecoding.tv' from='{name}@livecoding.tv' type='groupchat' id='36' xmlns='jabber:client'><body xmlns='jabber:client'>{message}</body><x xmlns='jabber:x:event'><composing/></x></message>"

		self.connection.send(send_command.format(
			message=message,
			name=self.config['bot-name'],
			channel=self.config['channel'],
		))