#!/usr/bin/env python3
from tornado.ncss import Server
from tornado.template import Loader
import db

loader = Loader(".")


def index(response):
	indexhtml = loader.load("index.html")
	response.write(indexhtml.generate(names=db.get_names()))

def game_page(response, name):
	response.write("So you like to play " + name + "?")

def add_name_page(response):
	name = response.get_field("name")
	db.add_name(name)
	response.redirect("/")



server = Server()
server.register("/", index, post=add_name_page)
server.register("/game/([A-Z][a-z]*)", game_page)

db.init()

server.run()