#!/usr/bin/env python3
from tornado.ncss import Server
from tornado.template import Loader
import db

loader = Loader(".")
#loader = Loader("./templates")

def index(response):
	indexhtml = loader.load("index.html")
	response.write(indexhtml.generate(names=db.get_names()))

def register(response):
	registerhtml = loader.load("register.html")
	response.write(registerhtml)

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
		response.set_secure_cookie("username", username) 
		response.redirect("/")
	else:
		response.redirect("/")

def register_user(response):
	username = response.get_field("username")
	#name = response.get_filed("name")
	if not user_exists:
		db.add_player(username)




server = Server()
#server.register("/", index, post=add_name_page)
server.register("/", index, post=login_user)
server.register("/register", register, post=register_user)
server.register("/game/([A-Z][a-z]*)", game_page)

db.init()

server.run()