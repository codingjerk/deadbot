# Base scraper

from extensions import base

class Scraper(base.Extension):
	def __init__(self):
		super().__init__({})

	def can_be_scraped(self, song):
		return False

	def scrap(self, song_title_or_url):
		pass