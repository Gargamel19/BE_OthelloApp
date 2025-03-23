import uuid
from app.models import OthelloGame, Move, GameMode
from datetime import datetime
from app.extentions import db
from sqlalchemy import or_, and_
import random


class GameManager:
    def __init__(self):
        self.games = {}  # Store games by game ID

    def fromGameID(self, game_id: uuid.UUID):
        game = OthelloGame.query.filter_by(id=game_id).first()
        board = self.initialize_board()
        moves = Move.query.filter_by(game_id=game_id).all()
        for move in moves:
            self.make_move(game_id, move.player_id, move.coordA, move.coordN)

        return game, board


    def create_game(self, white_id: uuid.UUID, black_id: uuid.UUID, game_mode: GameMode):
        game= OthelloGame(white_id=white_id, black_id=black_id, created_date=datetime.now(), state="running", turn=1, game_mode=game_mode.value)
        db.session.add(game)
        db.session.commit()
        return game.id
    

    def initialize_board(self):
        board = [["." for _ in range(8)] for _ in range(8)]
        board[3][3] = 0
        board[3][4] = 1
        board[4][3] = 1
        board[4][4] = 0
        return board

    def build_board(self, game_id: uuid.UUID):
        
        # Get game and board
        game = OthelloGame.query.filter_by(id=game_id).first()
        board = self.initialize_board()
        current_turn = 1
        # Apply all moves that are not tracked
        for move in game.moves:
            x = ord(move.coordA.lower()) - ord('a')
            y = move.coordN - 1
            board[y][x] = move.color
            captured_pieces = self.get_captured_pieces(board, move.color, x, y)

            if board[y][x] == "." and not captured_pieces:
                raise ValueError("Invalid move")

            self.flip_pieces(board, move.color, captured_pieces)
            current_turn = 0 if current_turn == 1 else 1

        game.turn = current_turn
        db.session.commit()

        return game, board

    def check_game_over(self, game: OthelloGame, board: list):
        legal_moves = self.get_legal_moves(board, game.turn)
        if len(self.get_legal_moves(board, game.turn)) == 0:
            self.endGame(game, board)
            return True, legal_moves
        return False, legal_moves

    def make_random_move(self, game_id: uuid.UUID):
        game, board = self.build_board(game_id)
        end, legal_moves = self.check_game_over(game, board)
        if end:
            return
        else:
            random.shuffle(legal_moves)
            move = legal_moves[0]
            get_char = chr(ord('a') + move[0])
            self.make_move(game_id, None, get_char, move[1]+1, len(game.moves) + 1)
             #TODO: Check if game is over
        game, board = self.build_board(game_id)
        end, legal_moves = self.check_game_over(game, board)
            

    def get_legal_moves(self, board: list, turn: int):
        legal_moves = []
        for x in range(8):
            for y in range(8):
                if board[y][x] == ".":
                    captured_pieces = self.get_captured_pieces(board, turn, x, y)
                    if len(captured_pieces) > 0:
                        legal_moves.append((x, y))
        return legal_moves


    def endGame(self, game: OthelloGame, board: list):
        white_count = 0
        black_count = 0
        for row in board:
            for cell in row:
                if cell == 0:
                    white_count += 1
                elif cell == 1:
                    black_count += 1

        if white_count > black_count:
            game.state = "white won"
        elif white_count < black_count:
            game.state = "black won"
        else:
            game.state = "draw"
        db.session.commit()
        return game.state

    def make_move(self, game_id: uuid.UUID, player_id: uuid.UUID, coordA: str, coordN: int, move_number: int):
        
        game, board = self.build_board(game_id)

        if move_number != len(game.moves) + 1:
            raise ValueError("Invalid move number")

        if player_id != None and ((game.turn == 1 and player_id == game.black_id) or \
           (game.turn == 0 and player_id == game.white_id)):
            print("Not your turn")
            raise ValueError("Not your turn")

        x = ord(coordA.lower()) - ord('a')
        y = coordN - 1

        captured_pieces = self.get_captured_pieces(board, game.turn, x, y)


        if board[y][x] != "." or not captured_pieces:
            print("Invalid move")
            raise ValueError("Invalid move")
        
        board[y][x] = game.turn

        self.flip_pieces(board, game.turn, captured_pieces)
        fen = self.compute_fen(board)

        move = Move(game_id=game_id, move_number=move_number, coordA=coordA, coordN=coordN, color=game.turn, player_id=player_id, fen=fen)
        db.session.add(move)

        print("Player", player_id, "made move", coordA, coordN,)
        print("in game", game_id)
        self.print_game(board)

        game.turn = 0 if game.turn == 1 else 1
        db.session.commit()

        game, board = self.build_board(game_id)
        self.check_game_over(game, board)

        return game, board
    
    def flip_pieces(self, board: list, turn: int, captured_pieces_list: list):
        for captured_positions in captured_pieces_list:
            for x, y in captured_positions:
                board[y][x] = turn

    def get_captured_pieces(self, board: list, turn: int, x: int, y: int):
        opponent_color = 1 if turn == 0 else 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

        captured_positions_return = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            captured_positions = []

            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[ny][nx] == opponent_color:
                    captured_positions.append((nx, ny))
                elif board[ny][nx] == turn:
                    for entry in captured_positions:
                        captured_positions_return.append([entry])
                    break
                else:
                    break

                nx += dx
                ny += dy
        return captured_positions_return
    
    def compute_fen(self, board):
        out_fen = ""
        for row in board:
            for cell in row:
                out_fen += str(cell)
            out_fen += "/"
        return out_fen
    
    def resign_game(self, game_id, player_id):
        game = OthelloGame.query.filter_by(id=game_id).first()
        if game.white_id == player_id:
            game.state = "black won"
        else:
            game.state = "white won"
        db.session.commit()
    
    def print_game(self, board): 
        print("\n".join([" ".join([str(cell) for cell in row]) for row in board]))