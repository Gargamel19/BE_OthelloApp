from flask.blueprints import Blueprint 

game_bp = Blueprint('game', __name__, template_folder='templates', url_prefix='/game')

import app.game.routes