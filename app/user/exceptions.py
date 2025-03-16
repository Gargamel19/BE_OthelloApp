from werkzeug import exceptions

class UserNOTExist(exceptions.HTTPException):
    code = 404
    description = 'User dose not exist.'

class UserAlreadyExist(exceptions.HTTPException):
    code = 400
    description = 'User dose already exist.'