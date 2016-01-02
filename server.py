#!/usr/bin/env python3
from tornado.ncss import Server
from tornado.template import Loader
import db
import random
import string
from collections import namedtuple

loader = Loader(".")
#loader = Loader("./templates")

######################################################################################################
### HTML Page stuff that uses the templates ###

def index_page(response):
  indexhtml = loader.load("index.html")
  response.write(indexhtml.generate(names=db.get_names()))

def join_game_page(response):
  join_game_html = loader.load("join_game.html")
  response.write(join_game_html.generate(username=get_user(response)))

def lobby_page(response, roomcode):
  in_game = player_in_game(response, roomcode)
  print(in_game)
  if in_game:
    lobbyhtml = loader.load("lobby.html")
    response.write(lobbyhtml.generate(code=roomcode, game_players=db.get_game_players(roomcode)))
  else:
    response.redirect("/join_game")

#################################################################################################
### Stuff for logining in, register, using cookies ###

def login_post(response):
  username = response.get_field("username")
  user_exists = db.user_exists(username)
  if user_exists:
    player_id = db.get_player_id(username)
    login_cookies(response, username, player_id)
  else:
    response.redirect("/")

def login_cookies(response, username, player_id):
  response.set_secure_cookie("username", username) 
  response.set_secure_cookie("player_id", str(player_id))
  response.redirect("/join_game")

def register_user_post(response):
  username = response.get_field("username")
  if not db.user_exists(username):
    player_id = db.add_player(username)
    login_cookies(response, username, player_id)

def get_user(response):
  username = response.get_secure_cookie("username")
  return username

def get_player_id_cookies(response):
  return int(response.get_secure_cookie("player_id"))

######################################################################################################
### Stuff for creating and joining a game room ###

def create_game_post(response):
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

def randomword(length):
  return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(length))

def join_game_post(response):
  code = response.get_field("roomcode")
  join_lobby(response, code)

def game_page(response, roomcode):
  words = ['Fishing', 'Half', 'Coach', 'Mop', 'Laugh', 'Nature', 'Brand', 'Sandwich', 'Implode', 'Sip', 'Gallop', 'Unemployed', 'Ditch', 'Engine', 'Fringe', 'Corduroy', 'Knife', 'Candy', 'Stick', 'Sick', 'Lyrics', 'Cook', 'Elephant', 'Campsite', 'Mine']
  colours = ['red', 'red', 'neutral', 'blue', 'neutral', 'neutral', 'red', 'black', 'blue', 'blue', 'neutral', 'neutral', 'neutral', 'neutral', 'red', 'blue', 'neutral', 'neutral', 'blue', 'neutral', 'blue', 'blue', 'red', 'neutral', 'red']
  guessed = [False, True, False, False, False, True, False, False, True, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False]
  CodeName = namedtuple('CodeName', 'word colour position guessed')
  Player = namedtuple('Player', 'name team spymaster')
  codenames = [CodeName(**{'word': word, 'colour': colour, 'position': position, 'guessed': guess}) for word, colour, position, guess in zip(words, colours, range(25), guessed)]
  player = Player(name='Test', team='blue', spymaster=True)
  gamehtml = loader.load("templates/game.html")
  response.write(gamehtml.generate(code=roomcode, codenames=codenames, player=player))
  

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

######################################################################################################
### Stuff for starting to play the game ###

def start_game_post(response, roomcode):
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

def assign_teams_and_roles(roomcode):
  players = db.get_game_players(roomcode)
  random.shuffle(players)
  colours =  []
  game_id = db.get_active_game_id(roomcode)
  for i in len(players):
    if i < 2:
      if i % 2 == 0:
        db.update_game_player(game_id, player_id, "blue", "True")
      else:
        db.update_game_player(game_id, player_id, "red", "True")
    else:
      if i % 2 == 0:
        db.update_game_player(game_id, player_id, "blue", "False")
      else:
        db.update_game_player(game_id, player_id, "red", "False")

#########################################################################
### General Database checking functions for everywhere ###

def player_in_game(response, roomcode):
  player_id = get_player_id_cookies(response)
  in_game = db.player_in_game(player_id, roomcode)
  return in_game


server = Server()
#server.register("/", index, post=add_name_page)
server.register("/", index_page)
server.register("/register", register_user_post)
server.register("/login", login_post)
server.register("/join_game", join_game_page)
server.register("/game/create", create_game_post)
server.register("/game/join", join_game_post)
server.register("/lobby/([a-z]+)", lobby_page)
server.register("/game/([a-z]+)", game_page)
server.register("/game/startgame/([a-z]+)", start_game_post)
server.register("/game/([a-z]+)", game_page)

db.init()

server.run()
