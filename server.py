#!/usr/bin/env python3
from tornado.ncss import Server

indexhtml = open("index.html").read()

def index(response):
	response.write(indexhtml)

def gamepage(response, name):
	response.write("So you like to play " + name + "?")

server = Server()
server.register("/", index)
server.register("/game/([A-Z][a-z]*)", gamepage)

server.run()