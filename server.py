#!/usr/bin/env python3
import sqlite3
from tornado.ncss import Server
from tornado.template import Loader

loader = Loader(".")


conn = sqlite3.connect('codenames.db', isolation_level=None)

def create_players_table():
	conn.execute("""CREATE TABLE IF NOT EXISTS players (
		name TEXT PRIMARY KEY
	)""")

def get_names():
	cursor = conn.execute("SELECT * FROM players")
	tuples = cursor.fetchall()
	names = [name for name, in tuples]
	return names

def add_name(name):
	conn.execute("INSERT INTO players VALUES (?)", (name,))

def index(response):
	indexhtml = loader.load("index.html")
	response.write(indexhtml.generate(names=get_names()))

def game_page(response, name):
	response.write("So you like to play " + name + "?")

def add_name_page(response):
	name = response.get_field("name")
	add_name(name)
	response.redirect("/")



server = Server()
server.register("/", index, post=add_name_page)
server.register("/game/([A-Z][a-z]*)", game_page)

create_players_table()
server.run()