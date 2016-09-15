# Youtube scraper

from extensions import base

import itertools

import requests
from urllib import parse
from lxml import etree

# TODO: use base.Scraper
class Scraper(base.Extension):
	def __init__(self):
		super().__init__({})

	def is_url(self, song):
		protocols = ['http', 'https']
		hosts = ['youtube.com', 'youtu.be']
		prefixes = ['', 'www.']

		for e in itertools.product(protocols, hosts, prefixes):
			if song.startswith('{}://{}{}/watch?v='): return True

		return False

	def scrap(self, song_title_or_url):
		if self.is_url(song_title_or_url):
			url = song_title_or_url
		else:
			url = self.get_song_url(song_title_or_url)

		# TODO: return None if url requested, but its not youtube url
		# TODO: return None if scraping was unsuccessful
		title = self.get_song_title(url)
		return url, title

	def get_song_title(self, song_url):
		data = requests.get(song_url).text
		return self.extract_song_title(data)

	def get_song_url(self, song_title):
		search_url = 'https://www.youtube.com/results?search_query={song}'.format(song=parse.quote(song_title))
		data = requests.get(search_url).text

		return self.extract_song_url(data)

	# TODO: process errors
	def extract_song_title(self, html):
		root = self.parse_html(html)
		meta_nodes = root.xpath('.//meta[@property="og:title"]')
		return meta_nodes[0].attrib['content']

	# TODO: process errors
	def extract_song_url(self, html):
		root = self.parse_html(html)
		link_nodes = root.xpath('.//h3[@class="yt-lockup-title "]/a')
		return 'https://youtube.com{url_part}'.format(
			url_part=link_nodes[0].attrib['href']
		)
		
	def parse_html(self, html):
		html_parser = etree.HTMLParser()
		return etree.fromstring(html, parser=html_parser)