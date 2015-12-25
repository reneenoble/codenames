#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('codenames.db', isolation_level=None)

def init():
	create_players_table()
	create_games_table()
	create_game_players_table()
	create_words_table()
	create_game_words_table()

def create_players_table():
	conn.execute("""CREATE TABLE IF NOT EXISTS players (
		player_id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT, 
		password TEXT
	)""")

def create_games_table ():
	conn.execute("""CREATE TABLE IF NOT EXISTS games (
		game_id INTEGER PRIMARY KEY AUTOINCREMENT,
		room_code CHAR(4),
		game_state text
		)""")

def create_game_players_table():
	conn.execute("""CREATE TABLE IF NOT EXISTS game_players (
		game_id INTEGER,
		player_id INTEGER,
		nickname TEXT,
		team TEXT,
		spymaster BOOLEAN,
		PRIMARY KEY (game_id, player_id),
		FOREIGN KEY (game_id) REFERENCES games(game_id),
		FOREIGN KEY (player_id) REFERENCES players(player_id)
		)""")

def create_words_table():
	conn.execute("""CREATE TABLE IF NOT EXISTS words (
		word TEXT PRIMARY KEY
		)""")

def create_game_words_table():
	conn.execute("""CREATE TABLE IF NOT EXISTS game_words (
		game_id INTEGER, 
		word TEXT,
		colour TEXT,
		position INTEGER,
		guessed BOOLEAN,
		FOREIGN KEY (game_id) REFERENCES games(game_id),
		FOREIGN KEY (word) REFERENCES words(word)
		)""")

def get_names():
	cursor = conn.execute("SELECT * FROM players")
	tuples = cursor.fetchall()
	names = [name for name, in tuples]
	return names

def add_name(name):
	conn.execute("INSERT INTO players VALUES (?)", (name,))

