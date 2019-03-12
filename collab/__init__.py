"""
contains the flask app and driver methods
"""

import os
import coloredlogs
import pydash
import logging.config

from ruamel.yaml import YAML
from flask import Flask, current_app

from .config import BasicConfig, ProdConfig
from .post_requests import add

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

    # adding blueprints
    app.register_blueprint(add)

    return app

def config_logging():
    """
    [summary]
    
    [description]
    
    """

    yaml = YAML(typ="safe")
    with current_app.open_resource(current_app.config['LOGGING_CONFIG']) as f:
        config = yaml.load(f)

    # check if debug data to be output
    log_lvl = "INFO"
    if os.environ.get('VERLOOP_DEBUG', False):
        log_lvl = "DEBUG"
    
    update_config = {
            "handlers":
            {
                "console":
                {
                    "level": log_lvl
                },
                "file":
                {
                    "filename": current_app.config['LOGS']
                }
            }
        }

    pydash.merge(config, update_config)

    logging.config.dictConfig(config)
    LOG.debug("Logger Configured!")