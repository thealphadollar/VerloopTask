"""
contains the flask app and driver methods
"""

import os
import yaml
import coloredlogs
import logging

from flask import Flask, current_app

from .config import BasicConfig, ProdConfig


LOG = logging.getLogger("collab")

def create_app():
    """
    driver method for assembling all configuration
    and logging

    :return: server app
    :rtype: Flask App
    """
    LOG.DEBUG("Initialising flask module...")
    app = Flask(__name__, instance_relative_config=True)
    if os.environ.get("FLASK_APP_MODE", "dev").lower() == "production":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(BasicConfig)
    # context intialized early to setup database and other related services
    app.app_context().push()

    try:
        os.makedirs(current_app.config['DIR'], exist_ok=True)
    except OSError as err:
        LOG.DEBUG(err)
        LOG.ERROR("Error: Unable to create %s", current_app.config['DIR'])
        LOG.WARNING("Initialisation aborted!")

    LOG.DEBUG("Initialising logging module...")
    config_logging()

    return app

def config_logging():
    """
    [summary]
    
    [description]
    
    """

    with current_app.open_resource('logging.YAML') as f:
        config = yaml.safe_load(f.read())

    # check if debug data to be output
    log_lvl = "INFO"
    if os.environ.get('VERLOOP_DEBUG', False):
        log_lvl = "DEBUG"
    config.update(
        {
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
    )

    logging.config.dictConfig(config)
    LOG.DEBUG("Logger Configured!")