from werkzeug import exceptions

class GameNOTExist(exceptions.HTTPException):
    code = 404
    description = 'Game dose not exist.'

class GameAlreadyExist(exceptions.HTTPException):
    code = 400
    description = 'Game dose already exist.'

class InvalidMove(exceptions.HTTPException):
    code = 400
    description = 'Invalid move.'