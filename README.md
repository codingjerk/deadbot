# DeadBot

DeadBot is simple selenium-based Livecoding.tv chat bot.

## Dependencies

- Python 3
- Python libraries:
	- lxml
	- validators
	- requests
	- websocket
- Your own or separate bot's account on streaming platform
- Command line

## Installation and usage

### 1. Install dependencies
```
$ sudo pip install -r requirements.txt
```

### 2. Copy default config file
```
$ cp config.json ~/.deadbot.json
```

### 3. Edit your own configuration
```
$ vim ~/.deadbot.json
```

*Note: use your favorite editor*

### 4. Run
```
$ ./deadbot
```
or
```
$ python deadbot.py
```
also you can specify config file directly:
```
$ ./deadbot myconfig.json
```

*Note: also you can use external tool with GUI, but now it's not ready*

## Configuration

All configurable settings stored in your config file (~/.deadbot.json by default).

This file has separate *manager*, *engine* and *extensions* sections.

### Manager section

Here is global settings that uses to configure whole application:
- `command-prefix` -- prefix walking in front of each command, as example with prefix `!` help command will looks like `!help`
- `message-format` -- how will looks text sended by bot, as example with `I say: {text}`, then bot says `hi`, it will be displayed like `I say: hi`
- `greeting` -- message, which bot will send when he will be connected, can be removed
- `parting` -- message, which bot will send before he will be disconnected, can be removed

### Engine section

Engine section contains information about using service, channel and authorization data.

#### Supported services

Currently Deadbot supports only Livecoding.tv, but I'll add twitch.tv support soon.

#### Options
- `service` -- service which bot will use
- `channel` -- your channel name
- `bot-name` -- name of bot's account on specified service
- `bot-key` -- bot's account's key (see *Getting Livecoding.tv key* to get more info)
- `bot-key-file` -- alternative to `bot-key` if you want to use external file with key
- `ignore-own-messages` -- by default bot will not react on own messages, but this can be disabled, because it's usefull, especialy if you use our own account for bot

#### Getting Livecoding.tv key

*Note: Livecoding.tv key is secret, never share it with outsiders.*

To get livecoding.tv key:
1. Open any livecoding.tv channel with chat
1. Open developer tools and start recording network events
1. Find WebSockets event
1. Open WebSockets frames
1. Find frame (it must be 4-rd) with similar content:
	- `<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>HERE IS YOUR KEY</auth>`

### Extensions

Here is a bunch of included extensions with it's own configuration:

#### Spammer

Spammer is extension which sends random messages in random interval with configured send chance.

- `phrases` -- list of phrases which bot will say sometimes
- `chance` -- number (from 0 to 1) sets, how often bot will spam (as example 1/60 is aprox 1 message in minute)

#### Greeter

Greeter is extension which sends message then viewer joins chat.

- `greetings` -- list of phrases to say. You can use following patterns in phrases:
	- `{user}` -- name of user which joined

#### Commands

Commands is extension that allow to add simple text commands.

Format is `"command-name": {COMMAND OPTIONS}`.

Commands options is:
- `answer` -- how to answer on command. You can use following patterns:
	- `{user}` -- user which send command
	- `{args` -- arguments passed with command, as example for `!say something intresing` arguments is `"something intresing"`
- `description` -- how to display command in help
- `args` -- how to display arguments in help

##### Default commands
- `hi` - says `"Hi, username"`
- `say WHAT` - says anything
- `version` - just says 0.1

#### Player Control

Player control is extension that allow to listen music from deadbot (via external player) and control music througth chat.

##### Options
- `player` -- name of external player to use, now only mpv supported
- `scraper` -- name of service which will be used to take music from, now only youtube supported
- `playing-format` -- phrase which bot will say then it will play new song. You can use following patterns:
	- `{title}` -- title of song
	- `{url}` -- url from which the music is played
- `adding-format` -- phrase which bot will say then some user will add song to playlist. You can use following patterns:
	- `{song}` -- song name
- `failure-format` -- phrase which bot will say then he can't play song. You can use following patterns:
	- `{song}` -- song name

- `fallback-playlist` -- list of songs which will be used with empty user-driven playlist

##### Commands

- `play SONG` -- adds song to playlist
- `song` -- shows current song
- `playlist` -- shows current user-driven and fallback playlists