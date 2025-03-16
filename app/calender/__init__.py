from flask.blueprints import Blueprint 

calender_bp = Blueprint('calender', __name__, template_folder='templates', url_prefix='/calender')

import app.calender.routes