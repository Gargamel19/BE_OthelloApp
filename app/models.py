from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.extentions import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy_serializer import SerializerMixin



class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(1000), unique=True)
    firstname = Column(String(1000), nullable=False)
    lastname = Column(String(1000), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(1000), nullable=False)
    user_type = Column(Integer, nullable=False) #user=0, admin=1

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'lastname': self.lastname,
            'email': self.email,
            'user_type': self.user_type
        }


class OthelloGame(db.Model, SerializerMixin):
    
    __tablename__ = "othello_game"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    white_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    white = db.relationship('User', foreign_keys=[white_id], cascade='all')
    black_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    black = db.relationship('User', foreign_keys=[black_id], cascade='all')
    created_date = Column(DateTime, nullable=False)
    turn = Column(Integer, nullable=False, default=1)

    state = Column(String, nullable=False)
    
    moves = db.relationship('Move', back_populates='game', cascade='all, delete-orphan')


    def verify_move(self, move):
        return True

    def update_moves(self, move):
        if self.verify_move(move):
            self.moves.append(move)
        else:
            raise Exception("Invalid move")

    def to_dict(self):
        move_list= []
        for move in self.moves:
            move_list.append(move.to_dict())
        if self.turn == 1:
            turn = self.white_id
        else:
            turn = self.black_id

        return {
            'id': self.id,
            'white': self.white.to_dict(),
            'black': self.black.to_dict(),
            'moves': move_list,
            'created_date': self.created_date.isoformat(),
            'state': self.state,
            'turn': turn

        }
    
class Move(db.Model, SerializerMixin):

    __tablename__ = "move"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey('othello_game.id'))
    move_number = Column(Integer, nullable=False)
    coordN = Column(Integer, nullable=False)
    coordA = Column(String(1), nullable=False)
    color = Column(Integer, nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    fen = Column(String(1000), nullable=False)

    game = db.relationship('OthelloGame', back_populates='moves')

    def to_grid(self):
        return (self.coordN - 1, self.translation[self.coordA])

    def to_dict(self):
        return {
            'id': str(self.id),
            'game_id': str(self.game_id),
            'move_number': self.move_number,
            'coord': self.coordA + str(self.coordN),
            'player_id': str(self.player_id),
            'fen': self.fen
        }