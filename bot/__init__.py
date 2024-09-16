from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from .config import Config


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    bot = Flask(__name__)
    bot.config.from_object(Config)

    # разрешено всем доменам 
    CORS(bot, resources={r"/*": {"origins": "*"}})
    # разрешено определенным доменам 
    # CORS(bot, resources={r"/*": {"origins": ["http://example.com", "http://127.0.0.1:4042:5500"]}})

    
    db.init_app(bot)
    migrate.init_app(bot, db)

    from .urls import bot as bot_blueprint
    bot.register_blueprint(bot_blueprint)
    
    return bot
