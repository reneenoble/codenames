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

def lobby(response, roomcode):
  in_game = player_in_game(response, roomcode)
  print(in_game)
  if in_game:
    lobbyhtml = loader.load("lobby.html")
    response.write(lobbyhtml.generate(code=roomcode, game_players=db.get_game_players(roomcode)))
  else:
    response.redirect("/game")

def game_page(response, name):
  response.write("So you like to play " + name + "?")

def add_name_page(response):
  name = response.get_field("username")
  db.add_player(name)
  response.redirect("/")

def login_page(response):
  username = response.get_field("username")
  user_exists = db.user_exists(username)
  if user_exists:
    player_id = db.get_player_id(username)
    login(response, username, player_id)
  else:
    response.redirect("/")

def login(response, username, player_id):
  response.set_secure_cookie("username", username) 
  response.set_secure_cookie("player_id", str(player_id))
  response.redirect("/game")

def register_user(response):
  username = response.get_field("username")
  if not db.user_exists(username):
    player_id = db.add_player(username)
    login(response, username, player_id)

def get_user(response):
  username = response.get_secure_cookie("username")
  return username

def create_game(response):
  code_in_use = True
  while code_in_use:
    #create a roomcode, 
    code = randomword(4)
    #check if code is in use
    code_in_use = db.room_code_in_use(code)
  #add it to the database of room codes
  game_id = db.create_game(code)
  #add the player to the games_players table for this room redirect to the lobby for the room code
  join_lobby(response, code)

def join_game(response):
  code = response.get_field("roomcode")
  join_lobby(response, code)

def join_lobby(response, roomcode):
  #check if room code exists and what it's status is
  state = db.get_game_state(roomcode)
  if state == "lobby":
    game_id = db.get_active_game_id(roomcode)
    #add player to game players table
    player_id = get_player_id_cookies(response)
    db.add_game_player(game_id, player_id)
    #redirect to lobby page
    response.redirect("/lobby/" + roomcode)
  elif state == "playing":
    #The game in this room has already started. 
    print("The game in this room has already started. ")
  else:
    #You must either have the wring room code or the game you want has already finished
    print("You must either have the wrong room code or the game you want has already finished")

def start_game(response, roomcode):
  #If player in game
  if player_in_game(response, roomcode):
  #If game already started go to the game board
    if game_started(roomcode):

      #Otherwise start game
      #change game state to playing
      
      #assign players randomly to teams and to spymaster
      assign_teams_and_roles(roomcode)
      #choose words for the game
      #redirect to the game board
    else:
      response.redirect("game/play/roomcode")

  else:
    response.redirect("/game")

def randomword(length):
  return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(length))

def get_player_id_cookies(response):
  return int(response.get_secure_cookie("player_id"))

def player_in_game(response, roomcode):
  player_id = get_player_id_cookies(response)
  in_game = db.player_in_game(player_id, roomcode)
  return in_game


server = Server()
#server.register("/", index, post=add_name_page)
server.register("/", index)
server.register("/register", register_user)
server.register("/login", login_page)
server.register("/game", game, post=game)
server.register("/game/create", create_game)
server.register("/game/join", join_game)
server.register("/lobby/([a-z]+)", lobby)

db.init()

server.run()