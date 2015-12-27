#!/usr/bin/env python3
from tornado.ncss import Server
from tornado.template import Loader
import db
import random
import string

loader = Loader(".")
#loader = Loader("./templates")

def index(response):
	indexhtml = loader.load("index.html")
	response.write(indexhtml.generate(names=db.get_names()))

def register(response):
	registerhtml = loader.load("register.html")
	response.write(registerhtml)

def game(response):
	gamehtml = loader.load("game.html")
	response.write(gamehtml.generate(username=get_user(response)))

def lobby(response):
	lobbyhtml = loader.load("lobby.html")
	response.write(lobbyhtml.generate(players=get_game_players(code)))

def game_page(response, name):
	response.write("So you like to play " + name + "?")

def add_name_page(response):
	name = response.get_field("username")
	db.add_player(name)
	response.redirect("/")

def login_user(response):
	username = response.get_field("username")
	user_exists = db.user_exists(username)
	print("printing1", user_exists)
	if user_exists:
		player_id = db.get_player_id(username)
		print(username, type(player_id))
		response.set_secure_cookie("username", username) 
		response.set_secure_cookie("player_id", str(player_id))
		response.redirect("/game")
	else:
		response.redirect("/")

def register_user(response):
	username = response.get_field("username")
	#name = response.get_filed("name")
	if not user_exists:
		db.add_player(username)

def get_user(response):
	username = response.get_secure_cookie("username")
	return username


def get_player_id_cookies(response):
	return int(response.get_secure_cookie("player_id"))

server = Server()
#server.register("/", index, post=add_name_page)
server.register("/", index, post=login_user)
server.register("/register", register, post=register_user)
server.register("/game", game, post=game)
server.register("/game/create", create_game)
server.register("/game/join", join_game)
server.register("/lobby/([A-Z]+)", game_page)

db.init()

server.run()