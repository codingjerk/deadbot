#!/usr/bin/env python

import sys
import json

import parser

def log_exception(exception):
	print(exception)

def observe(function):
	try: function()
	except Exception as exception: log_exception(exception)

def get_config(args):
	if len(args) == 1: config_file = args[0]
	else: config_file = '~/.deadbot.json'

	return json.load(open(config_file))

def main(args):
	config = get_config(args)

	# TODO: observe(parser.validate_config, config)
	manager = parser.build_manager(config)
	observe(manager.wait)

if __name__ == '__main__':
	main(sys.argv[1:])