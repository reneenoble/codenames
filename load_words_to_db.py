#!/usr/bin/env python3
import sqlite3
import db

#Loads wordlist to DB
conn = sqlite3.connect('codenames.db', isolation_level=None)

wordfile = "wordslist.txt"
words = []
with open(wordfile, "r") as f:
    for line in f:
        line = line.strip().lower()
        words.append(line)

db.add_words(words)
