from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.extentions import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy_serializer import SerializerMixin



class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = "user"
    id = Column(String(1000), unique=True, primary_key=True) # primary keys are required by SQLAlchemy
    username = Column(String(1000), unique=True)
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



class Calender(db.Model, SerializerMixin):
    __tablename__ = "calender"
    id = Column(String(1000), unique=True, primary_key=True) # primary keys are required by SQLAlchemy
    owner = mapped_column(ForeignKey("user.id"))
    name = Column(String(1000), nullable=False)
    created_date = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)


    def to_dict(self):
        print(self.owner)
        return {
            'id': self.id,
            'owner': User.query.filter(User.id==self.owner).first().to_dict(),
            'name': self.name,
            'created_date': self.created_date,
            'year': self.year
        }