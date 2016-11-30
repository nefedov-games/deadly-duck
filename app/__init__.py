
# Application package constructor

from config import config
from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.session_protection = "strong"
login_manager.login_view = "auth.Login"


def CreateApp( config_name ):
    app = Flask( __name__ )
    app.config.from_object( config[ config_name ] )
    config[ config_name ].InitApp( app )

    bootstrap.init_app( app )
    mail.init_app( app )
    moment.init_app( app )
    db.init_app( app )
    login_manager.init_app( app )

    # Blueprints registration
    from .main import main as main_blueprint
    app.register_blueprint( main_blueprint )

    from .auth import auth as auth_blueprint
    app.register_blueprint( auth_blueprint, url_prefix="/auth" )

    from .game import game as game_blueprint
    app.register_blueprint( game_blueprint, url_prefix="/game" )

    return app