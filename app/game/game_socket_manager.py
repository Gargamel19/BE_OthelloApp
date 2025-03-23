from flask_socketio import SocketIO, emit, join_room, leave_room
from game_manager import GameManager
from app import app
from app.models import GameMode


socketio = SocketIO(app, cors_allowed_origins="*")


# Queue for matchmaking
queue = []

@socketio.on('join_queue')
def join_queue(data):
    user_id = data['user_id']
    queue.append(user_id)

    # If there are at least two players in the queue, start a game
    if len(queue) >= 2:
        white_id = queue.pop(0)
        black_id = queue.pop(0)
        game_id, game = GameManager.create_game(white_id, black_id, game_mode=GameMode.ONLINE)

        # Notify both players about the game
        emit('game_started', {'game_id': game_id, 'game': game}, room=white_id)
        emit('game_started', {'game_id': game_id, 'game': game}, room=black_id)

@socketio.on('make_move')
def make_move(data):
    game_id = data['game_id']
    player_id = data['player_id']
    coordA = data['coordA']
    coordN = data['coordN']

    try:
        game = game_manager.make_move(game_id, player_id, coordA, coordN)
        emit('move_made', {'game_id': game_id, 'game': game}, broadcast=True)
    except ValueError as e:
        emit('error', {'message': str(e)})

@socketio.on('join_game')
def join_game(data):
    game_id = data['game_id']
    player_id = data['player_id']
    join_room(game_id)
    emit('joined_game', {'message': f'Player {player_id} joined game {game_id}'}, room=game_id)

@socketio.on('leave_game')
def leave_game(data):
    game_id = data['game_id']
    player_id = data['player_id']
    leave_room(game_id)
    emit('left_game', {'message': f'Player {player_id} left game {game_id}'}, room=game_id)
