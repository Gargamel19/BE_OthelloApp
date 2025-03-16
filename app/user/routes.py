from app.user import user_bp
from app.exceptions import *
from app.user.exceptions import *
from flask import render_template, redirect, url_for, request, flash, abort, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions
from app.models import User
from app.extentions import db, auth
from sqlalchemy.exc import IntegrityError
from flask import render_template_string
import uuid
import redis
from datetime import timedelta

from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, unset_refresh_cookies, unset_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash


@user_bp.errorhandler(exceptions.HTTPException)
def handle_error(e):
    return e.description, e.code

user_bp.register_error_handler(UserNOTExist, handle_error)
user_bp.register_error_handler(UserAlreadyExist, handle_error)
user_bp.register_error_handler(NotAuthorized, handle_error)


### API ENDPOINTS

# ------------------------------------------- LOGIN ---------------------------------------------------

    
@user_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):

        session_id = str(uuid.uuid4())

        add_claims = {
            'session_id': session_id,
            'username' : user.username,
            'email' : user.email,
            'user_type' : user.user_type,
        }

        access_token = create_access_token(identity=user.id, additional_claims=add_claims)
        refresh_token = create_refresh_token(identity=user.id, additional_claims=add_claims)
        return jsonify({'message': 'Login Success', 'access_token': access_token, 'refresh_token': refresh_token})
    else:
        return jsonify({'message': 'Login Failed'}), 401
    

@user_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    add_claims = {
        'session_id': refresh_token.get("session_id"),
        'username' : user.username,
        'email' : user.email,
        'user_type' : user.user_type,
    }

    access_token = create_access_token(identity=user.id, additional_claims=add_claims)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=add_claims)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

# ------------------------------------------- LOGOUT ---------------------------------------------------



# ------------------------------------------- USER RESSOURCE ---------------------------------------------------
# CREATE:

@user_bp.route('/', methods=['POST'])
def create_user():
    
    username = request.form["username"]
    lastName = request.form["lastName"]
    email = request.form["email"]
    pw = request.form["password"]
    password = generate_password_hash(pw, method="pbkdf2:sha256")

    try:
        user = User(id=str(uuid.uuid4), name=username, lastname=lastName, email=email, password=password, user_type=0)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        raise UserAlreadyExist()

    return user.to_dict()

# GET
@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    search_user = User.query.filter(User.id == user_id).first()
    if not search_user:
        raise UserNOTExist()
    return search_user.to_dict()

# UPDATE
@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def edit_user(user_id):

    user_id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=user_id).first()

    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise UserNOTExist()
    if not (user_id == logged_in_user.id or logged_in_user.user_type == 1):
        raise NotAuthorized()
    username = request.form["username"]
    firstName = request.form["firstName"]
    lastName = request.form["lastName"]
    email = request.form["email"]
    pw = request.form["password"]
    password = generate_password_hash(pw, method="pbkdf2:sha256")
    user.name = username
    user.firstName = firstName
    user.lastName = lastName
    user.email = email
    user.password = password
    db.session.add(user)
    db.session.commit()
    return user.to_dict()

# DELETE
@user_bp.route('/<public_id>', methods=['DELETE'])
@jwt_required()
def delete_user(public_id):
    
    user_id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=user_id).first()

    user = User.query.filter(User.id == public_id).first()
    if not user:
        raise UserNOTExist()
    if not (public_id == logged_in_user.id or logged_in_user.user_type == 1):
        raise NotAuthorized()
    db.session.delete(user)
    db.session.commit()
    return user.to_dict()

# PROMOTE
@user_bp.route('/<public_id>/promote', methods=['POST'])
@jwt_required()
def promote_user(public_id):
    
    user_id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=user_id).first()

    user = User.query.filter(User.id == public_id).first()
    if not user:
        raise UserNOTExist()
    if not (logged_in_user.user_type == 1):
        raise NotAuthorized()
    user.user_type=1
    db.session.commit()
    return user.to_dict()
