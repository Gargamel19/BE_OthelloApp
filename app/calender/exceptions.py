from werkzeug import exceptions

class CalenderNOTExist(exceptions.HTTPException):
    code = 404
    description = 'Calender dose not exist.'

class CalenderAlreadyExist(exceptions.HTTPException):
    code = 400
    description = 'Calender dose already exist.'