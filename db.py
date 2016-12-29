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
    username TEXT UNIQUE,
    display_name TEXT, 
    password TEXT
  )""")

def create_games_table ():
  #game states: lobby, playing, finished
  conn.execute("""CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_code CHAR(4),
    game_state TEXT,
    current_colour TEXT
    )""")

def create_game_players_table():
  conn.execute("""CREATE TABLE IF NOT EXISTS game_players (
    game_id INTEGER,
    player_id INTEGER,
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

def create_clues_table():
  conn.execute("""CREATE TABLE IF NOT EXISTS clues (
    clue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    clue TEXT,
    clue_maker INTEGER,
    FOREIGN KEY (clue_maker) REFERENCES players(player_id)
    )""")

def get_names():
  cursor = conn.execute("SELECT * FROM players")
  tuples = cursor.fetchall()
  names = [username for player_id, username, disp_name, pword in tuples]
  return names

def add_player(name):
  cursor = conn.execute("INSERT INTO players (username) VALUES (?)", (name,))
  player_id = cursor.lastrowid
  return player_id

def user_exists(username):
  cursor = conn.execute("SELECT * FROM players WHERE username = ?", (username,))
  users = cursor.fetchall()
  if users:
    return users[0][0]
  else:
    return None

def create_game(code):
  cursor = conn.execute("INSERT INTO games (room_code, game_state) VALUES (?, ?)", (code, "lobby"))
  game_id = cursor.lastrowid
  return game_id

def get_active_game_id(code):
  cursor = conn.execute("SELECT game_id FROM games WHERE room_code = ? AND game_state != 'finished'", (code,))
  game = cursor.fetchone()
  if game:
    game_id = game[0]
    return game_id
  else:
    return "not active"

def room_code_in_use(code):
  cursor = conn.execute("SELECT * FROM games WHERE room_code = ? AND game_state != ? ", (code, "finished"))
  games = cursor.fetchall()
  if games:
    return True
  else:
    return False

def get_game_state(code):
  cursor = conn.execute("SELECT * FROM games WHERE room_code = ? AND game_state != ? ", (code, "finished"))
  games = cursor.fetchall()
  if games:
    state = games[0][2]
    return state
  else:
    return("not active")

def get_game_state_by_id(game_id): 
  cursor = conn.execute("SELECT game_state FROM games WHERE game_id = ?", (game_id,))
  games = cursor.fetchone()
  if games:
    state = games[0]
    return state
  else:
    return None

def set_game_state_to_playing(game_id):
  cursor = conn.execute("UPDATE games SET game_state = 'playing' WHERE game_id=?", (game_id,))

def set_game_state_to_finished(game_id):
  cursor = conn.execute("UPDATE games SET game_state = 'finished' WHERE game_id=?", (game_id,))

def set_current_colour(game_id, colour):
  cursor = conn.execute("UPDATE games SET current_colour = ? WHERE game_id=?", (colour, game_id))

def add_game_player(game_id, player_id):
  conn.execute("INSERT INTO game_players (game_id, player_id) VALUES (?, ?)", (game_id, player_id))

def get_player_id(username):
  cursor = conn.execute("SELECT * FROM players WHERE username = ?", (username,))
  players = cursor.fetchall()
  if players:
    user_id = players[0][0]
    return user_id
  else:
    return None

def get_game_players(game_id):
  cursor = conn.execute("SELECT * FROM game_players WHERE game_id = ?", (game_id,))
  game_instances = cursor.fetchall()
  game_players = [conn.execute("SELECT * FROM players where player_id = ?", (i[1],)).fetchall()[0][1] for i in game_instances]
  return game_players

def player_in_game(player_id, code):
  game_id = get_active_game_id(code)
  cursor = conn.execute("SELECT * FROM game_players WHERE game_id = ? AND player_id = ?", (game_id, player_id))
  players = cursor.fetchall()
  if players:
    return True
  else:
    return False

def update_game_player(game_id, player_id, team, spymaster):
  conn.execute("UPDATE game_players SET team = ?, spymaster = ? WHERE game_id = ? AND player_id = ?", (team, spymaster, game_id, player_id))

def add_word(word):
  conn.execute("INSERT INTO words VALUES (?)", (word,))

def add_words(words):
  for word in words:
    add_word(word)

def random_words(number):
  cursor = conn.execute("SELECT * FROM words ORDER BY random() LIMIT ?", (number,))
  words_tup = cursor.fetchall()
  return [w[0] for w in words_tup]

def add_game_word_pair(game_id, word, colour, number):
  cursor = conn.execute("INSERT INTO game_words (game_id, word, colour, position, guessed) VALUES (?, ?, ?, ?, ?)", (game_id, word, colour, number, False))

def add_game_word_pairs(game_id, word_colour_pairs):
  for i, (w, c) in enumerate(word_colour_pairs):
    add_game_word_pair(game_id, w, c, i)
    
def get_game_words(game_id):
  cursor = conn.execute("SELECT word, colour, position, guessed FROM game_words WHERE game_id = ?", (game_id,))
  word_data = cursor.fetchall()
  return word_data
