from random import choice
from string import ascii_uppercase
from flask import Flask

app=Flask(__name__)
@app.route('/')
def add():
