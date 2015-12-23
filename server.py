
#!/usr/bin/env python3
from tornado.ncss import Server

def index(response):
	response.write("Welcome to Codenames")

def gamepage(response, name):
	response.write("So you like to play " + name + "?")

server = Server()
server.register("/", index)
server.register("/game/([A-Z][a-z]*)", gamepage)

server.run()