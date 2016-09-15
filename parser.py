from extensions import manager

def build_manager(config):
	engine = build_engine(config)
	extension_names, extensions = build_extensions(config)
	return manager.Manager(config['manager'], engine, extensions, extension_names)

def build_engine(config):
	if config['engine']['service'] == 'livecoding.tv':
		from engines import livecoding
		return livecoding.Engine(config['engine'])

def build_extensions(config):
	return zip(*[(name, build_extension(name, config))
		for name, config in config['extensions'].items()
	])

def build_extension(name, config):
	if name == 'spammer':
		from extensions import spammer
		return spammer.Extension(config)
	elif name == 'greeter':
		from extensions import greeter
		return greeter.Extension(config)
	elif name == 'commands':
		from extensions import commands
		return commands.Extension(config)
	elif name == 'player-control':
		player = build_player(config['player'])
		scraper = build_scraper(config['scraper'])
		from extensions import player_control
		return player_control.Extension(config, player, scraper)

def build_player(name):
	if name == 'mpv':
		from extensions.players import mpv
		return mpv.Player()

def build_scraper(name):
	if name == 'youtube':
		from extensions.scrapers import youtube
		return youtube.Scraper()