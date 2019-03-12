"""
handles configuration for two states of the flask app:
development and production
"""
import os

class BasicConfig:
    SECRET_KEY = 'dev'
    DIR = os.path.join(os.path.expanduser('~'), "collab")
    DATABASE = os.path.join(DIR, "collab.sql")
    LOGS = os.path.join(DIR, "collab.logs")
    LOGGING_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log_config.yaml")

class ProdConfig(BasicConfig):
    SECRET_KEY = 'skj123'