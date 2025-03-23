import click
from flask.cli import with_appcontext
from app.extentions import db
from .models import User
import uuid
from werkzeug.security import generate_password_hash
from .game.game_manager import GameManager

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    print("create tables")
    from app import create_app
    create_app()
    db.create_all()
    print("tables created")

def add_admin_h(username, firstname, lastname, email, pw, user_type=1):
    print("add_admin")
    password = generate_password_hash(pw, method="pbkdf2:sha256")
    newUser = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password, user_type=user_type)
    db.session.add(newUser)
    db.session.commit()

def add_user_h(username, firstname, lastname, email, pw, user_type=0):
    print("add_user")
    password = generate_password_hash(pw, method="pbkdf2:sha256")
    newUser = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password, user_type=user_type)
    db.session.add(newUser)
    db.session.commit()

@click.command(name='add_testdata')
@with_appcontext
def add_testdata():
    add_admin_h("fettarmqp", "ferdinand", "trendelenburg", "trendelenburger19.04@gmail.com", "1234", user_type=1)
    add_user_h("testuser", "testuser", "testuser", "testuser@gmail.com", "1234", user_type=0)

@click.command(name='test_game')
@with_appcontext
def test_game():
    from app.models import OthelloGame
    from app.models import User, GameMode
    from datetime import datetime
    import uuid

    temp_moves = ["d3", "c3", "b3", "b2"]

    user = User.query.all()
    gameManager = GameManager()
    gameID = gameManager.create_game(user[0].id, user[1].id, game_mode=GameMode.ONLINE)
    game, borad = gameManager.build_board(gameID)
    print("initial board")
    gameManager.print_game(borad)

    for x in range(len(temp_moves)):
        temp_move = temp_moves[x]
        if x % 2 == 1:
            _, borad = gameManager.make_move(gameID, user[1].id, temp_move[0], int(temp_move[1]), x+1)
        else:
            _, borad = gameManager.make_move(gameID, user[0].id, temp_move[0], int(temp_move[1]), x+1)
    
    print("game created")