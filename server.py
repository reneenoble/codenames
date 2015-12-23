#!/usr/bin/env python3
import sqlite3
from tornado.ncss import Server

indexhtml = open("index.html").read()

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


def index(response):
	response.write(indexhtml.format(", ".join(get_names())))

def gamepage(response, name):
	response.write("So you like to play " + name + "?")


server = Server()
server.register("/", index)
server.register("/game/([A-Z][a-z]*)", gamepage)

create_players_table()
server.run()