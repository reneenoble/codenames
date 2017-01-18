#!/usr/bin/env python3
from tornado.ncss import Server
from tornado.template import Loader
import db
import random
import string
from collections import namedtuple

loader = Loader("./templates")

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
  game_id = db.get_active_game_id(roomcode)
  word_data = db.get_game_words(game_id)
  CodeName = namedtuple('CodeName', 'word colour position guessed')
  Player = namedtuple('Player', 'name team spymaster')
  codenames = [CodeName(**{'word': word, 'colour': colour, 'position': position, 'guessed': guess}) for word, colour, position, guess in word_data]
  player = Player(name='Test', team='blue', spymaster=True)
  gamehtml = loader.load("game.html")
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
  elif state == "playing" or state == "endgame":
    #The game in this room has already started. 
    print("The game in this room has already started. ")
  else:
    #You must either have the wrong room code or the game you want has already finished and become historic
    print("You must either have the wrong room code or the game you want has already finished")

######################################################################################################
### Stuff for starting to play the game ###

def start_game_post(response, roomcode):
  game_id = db.get_active_game_id(roomcode)
  game_state = db.get_game_state_by_id(game_id)
  #If player in game
  if player_in_game(response, roomcode) and game_state != "not active":
    #If game already started go to the game board
    #Otherwise do start game procedure
    if game_state == "playing" or state == "endgame":
      response.redirect("game/play/" + roomcode)
    else:
      #change game state to playing
      db.set_game_state_to_playing(game_id)
      #assign players randomly to teams and to spymaster
      assign_teams_and_roles(game_id)
      #choose words for the game
      words = db.random_words(25)
      #who goes first?
      start_colour = random.choice(["blue", "red"])
      db.set_current_colour(game_id, start_colour)
      db.make_turn(game_id, start_colour)
      #assign card colours
      card_colours = [start_colour, "black"] + 7*["neutral"] + 8*["blue", "red"]
      random.shuffle(card_colours)
      #pair up words and colours
      pairs = zip(words, card_colours)
      db.add_game_word_pairs(game_id, pairs)
      
      #Send to game board
      response.redirect("/game/" + roomcode)

  else:
    response.redirect("/game")

def assign_teams_and_roles(game_id):
  players = db.get_game_players(game_id)
  player_ids = [db.get_player_id(p) for p in players]
  random.shuffle(player_ids)

  roles = [(colour, spy) for colour in ["blue", "red"] for spy in [True, False]] 

  for (player_id, (colour, spy_master)) in zip(player_ids, roles):
    db.update_game_player(game_id, player_id, colour, spy_master)

#########################################################################
### Things for playing the game live ###

def guess_word(room_code, player_id, word):
  #game_id
  game_id = db.get_active_game_id(room_code)
  game_state = db.get_game_state_by_id(game_id)
  if game_state == "playing":
    #Get player team
    player_team = db.player_team(game_id, player_id)
    #Is teams turn?
    turn = db.get_current_turn(game_id)
    if turn:
      turn_id, game_id, remaining_guesses, team = turn
      if remaining_guesses > 0 and player_team == team:
        #word changed to guessed
        colour, guessed_before = db.guess_word(game_id, word)
        if not guessed_before: 
          #num guesses reduced
          if colour == team:
            #reduce counter by 1
            db.set_guesses(turn_id, remaining_guesses - 1)
          elif colour == "black":
            #reduce counter to 0 and end game
            db.set_guesses(turn_id, 0)
            db.set_game_state_to_endgame(game_id)
            if player_team == "blue":
              winner = "red"
            elif player_team == "red":
              winner = "blue"
            db.set_winner(game_id, winner)
          else:
            #reduce counter to zero
            db.set_guesses(turn_id, 0)

        winner = get_game_winner(game_id)
        if winner:
          db.set_winner(game_id, winner)
          db.set_game_state_to_endgame(game_id)

def get_game_winner(game_id):
  game_state = db.get_game_state_by_id(game_id)
  if game_state == "playing":
    card_states = db.get_card_states(game_id)
    blue_win = all(i[1] for i in card_states if i[0] == "blue")
    red_win = all(i[1] for i in card_states if i[0] == "red")

    if blue_win:
      return "blue"
    elif red_win:
      return "red"
  
  

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


# room_code = "erco"
# player_id = 1
# word = "file"
# guess_word(room_code, player_id, word)