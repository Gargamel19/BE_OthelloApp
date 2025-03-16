from werkzeug import exceptions

class NotAuthorized(exceptions.HTTPException):
    code = 405 
    description = 'User is not authorized to perform this action'