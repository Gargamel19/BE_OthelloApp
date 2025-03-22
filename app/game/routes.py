from app.game import game_bp
from app.exceptions import *
from app.utils import *
from app.game.game_manager import GameManager
from app.game.exceptions import *
from flask import render_template, redirect, url_for, request, flash, abort, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions
from app.models import User, OthelloGame, Move
from app.extentions import db, auth, queue
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask import render_template_string
import uuid
from datetime import datetime

from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, unset_refresh_cookies, unset_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash

gameManager = GameManager()

@game_bp.errorhandler(exceptions.HTTPException)
def handle_error(e):
    return e.description, e.code

game_bp.register_error_handler(GameNOTExist, handle_error)
game_bp.register_error_handler(GameAlreadyExist, handle_error)
game_bp.register_error_handler(NotAuthorized, handle_error)


### API ENDPOINTS

# ------------------------------------------- LOGIN ---------------------------------------------------

@game_bp.route('', methods=['POST'])
@jwt_required()
def create_game():

    userID = get_jwt_identity()
    
    data = request.get_json()
    white_id = uuid.UUID(data['white_id'])
    black_id = uuid.UUID(data['black_id'])

    try:
        othelloGame = OthelloGame(white_id=white_id, black_id=black_id, created_date=datetime.now())
        db.session.add(othelloGame)
        db.session.commit()
    except IntegrityError:
        raise GameAlreadyExist()

    return jsonify(othelloGame.to_dict())	

@game_bp.route('', methods=['GET'])
@jwt_required()
def get_games():
    userID = uuid.UUID(get_jwt_identity())

    # Get pagination parameters from the query string
    page = request.args.get('page', 1, type=int)  # Default to page 1
    per_page = request.args.get('per_page', 10, type=int)  # Default to 10 items per page

    # Query games with pagination
    games_query = OthelloGame.query.filter(
        or_(OthelloGame.black_id == userID, OthelloGame.white_id == userID)
    ).order_by(OthelloGame.created_date.desc())

    # Apply pagination
    paginated_games = games_query.paginate(page=page, per_page=per_page, error_out=False)

    print(len(paginated_games.items))

    # Return paginated results
    return jsonify({
        "total": paginated_games.total,
        "page": paginated_games.page,
        "per_page": paginated_games.per_page,
        "games": [game.to_dict() for game in paginated_games.items]
    })
    
@game_bp.route('/<game_id>/resign', methods=['POST'])
@jwt_required()
def resign_game(game_id):
        game_id = uuid.UUID(game_id)
        data = request.get_json()
        player = data['player']
    
        gameManager.resign_game(game_id, uuid.UUID(player))
        return jsonify(OthelloGame.query.filter_by(id=game_id).first().to_dict())


@game_bp.route('/<game_id>/move', methods=['POST'])
@jwt_required()
def make_move(game_id):

    game_id = uuid.UUID(game_id)
    data = request.get_json()
    move = data['move']
    coordA = move[0]
    coordN = int(move[1])
    move_number = data['move_number']
    player = data['player']

    if player is None:
        return jsonify({"error": "player is null"}), 400

    try:
        gameManager.make_move(game_id, uuid.UUID(player), coordA, coordN, move_number)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify(OthelloGame.query.filter_by(id=game_id).first().to_dict())


@game_bp.route('/queue', methods=['GET'])
def get_queue():
    return jsonify(len(queue))

@game_bp.route('/queue/join', methods=['PUT'])
@jwt_required()
def search_game():

    userID = uuid.UUID(get_jwt_identity())
    user = User.query.filter_by(id=userID).first()
    if user not in queue:
        if len(queue) >= 1:
            gameManager.create_game(queue[0].id, userID)
            queue.pop(0)
        else:
            print(user.to_dict())
            queue.append(user)
        return jsonify({"message": "User added to queue"})
    else:
        return jsonify({"message": "User already in queue"}), 400

@game_bp.route('/queue/inqueue', methods=['GET'])
@jwt_required()
def inqueue():
    userID = uuid.UUID(get_jwt_identity())
    user = User.query.filter_by(id=userID).first()
    if user in queue:
        return jsonify(True)
    else:
        return jsonify(False), 404

@game_bp.route('/queue/leave', methods=['PUT'])
@jwt_required()
def desearch_game():
    userID = uuid.UUID(get_jwt_identity())
    user = User.query.filter_by(id=userID).first()
    print(user.to_dict())
    if user in queue:
        queue.remove(user)
    return jsonify({"message": "User deleted from queue"})

@game_bp.route('/open', methods=['GET'])
@jwt_required()
def get_open_games():
    print(len(queue))
    user = User.query.filter_by(id=uuid.UUID(get_jwt_identity())).first()
    games = OthelloGame.query.filter_by(state="running").filter(or_(OthelloGame.white_id == user.id, OthelloGame.black_id == user.id)).all()
    return jsonify([game.to_dict() for game in games])

@game_bp.route('/<game_id>', methods=['GET'])
def get_game(game_id):
    game_id = uuid.UUID(game_id)
    game = OthelloGame.query.filter_by(id=game_id).first()
    if game is None:
        raise GameNOTExist()
    return game.to_dict()

