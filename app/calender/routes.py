from app.calender import calender_bp
from app.exceptions import *
from app.utils import *
from app.calender.exceptions import *
from flask import render_template, redirect, url_for, request, flash, abort, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug import exceptions
from app.models import User, Calender
from app.extentions import db, auth
from sqlalchemy.exc import IntegrityError
from flask import render_template_string
import uuid
import redis
from datetime import datetime

from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies, unset_refresh_cookies, unset_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash


@calender_bp.errorhandler(exceptions.HTTPException)
def handle_error(e):
    return e.description, e.code

calender_bp.register_error_handler(CalenderNOTExist, handle_error)
calender_bp.register_error_handler(CalenderAlreadyExist, handle_error)
calender_bp.register_error_handler(NotAuthorized, handle_error)


### API ENDPOINTS

# ------------------------------------------- LOGIN ---------------------------------------------------

    
@calender_bp.route('', methods=['POST'])
@jwt_required()
def create_calender():

    userID = get_jwt_identity()
    
    data = request.get_json()
    name = data['name']
    year = data['year']

    try:
        calender = Calender(id=str(uuid.uuid4()), name=name, year=year, owner=userID, created_date=datetime.now())
        db.session.add(calender)
        db.session.commit()
    except IntegrityError:
        raise CalenderAlreadyExist()

    return jsonify(calender.to_dict())	

@calender_bp.route('/my', methods=['GET'])
@jwt_required()
def my_calender():
    userID = get_jwt_identity()
    calenders = Calender.query.filter_by(owner=userID).all()
    return jsonify(dict_helper(calenders))


@calender_bp.route('/all', methods=['GET'])
@jwt_required()
def all_calender():
    userID = get_jwt_identity()
    user = User.query.filter_by(id=userID).first()
    if not user or user.user_type != 1:
        raise NotAuthorized()
    calenders = Calender.query.all()
    return jsonify(dict_helper(calenders))