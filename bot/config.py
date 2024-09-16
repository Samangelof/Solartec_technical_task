import os
from dotenv import load_dotenv
from flask import current_app


load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GREEN_API_URL = os.getenv('GREEN_API_URL')
    GREEN_API_TOKEN = os.getenv('GREEN_API_TOKEN')
    GREEN_API_ID = os.getenv('GREEN_API_ID')

def green_api_config():
    return {
        'url': current_app.config['GREEN_API_URL'],
        'id': current_app.config['GREEN_API_ID'],
        'token': current_app.config['GREEN_API_TOKEN']
    }