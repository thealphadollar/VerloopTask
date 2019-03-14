"""
contains the flask app and driver methods
"""

import os
import logging

from flask import Flask, current_app

from .config import BasicConfig, ProdConfig
from .helpers import config_logging
from .post_requests import add
from .get_requests import stories
from .db_hanlder import DBHandler


LOG = logging.getLogger("collab")

def create_app():
    """
    driver method for assembling all configuration
    and logging

    :return: server app
    :rtype: Flask App
    """
    LOG.debug("Initialising flask module...")
    app = Flask(__name__, instance_relative_config=True)
    if os.environ.get("FLASK_ENV", "dev").lower() == "production":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(BasicConfig)
    # context intialized early to setup database and other related services
    app.app_context().push()

    try:
        os.makedirs(current_app.config['DIR'], exist_ok=True)
    except OSError as err:
        LOG.debug(err)
        LOG.error("Error: Unable to create %s", current_app.config['DIR'])
        LOG.warning("Initialisation aborted!")

    LOG.debug("Initialising logging module...")
    config_logging()

    # initialisating database
    DBHandler()

    # adding blueprints
    app.register_blueprint(add)
    app.register_blueprint(stories)

    return app