"""
contains methods that aid in the functioning of
main driving methods
"""

import os
import logging.config

import pydash

from ruamel.yaml import YAML
from flask import current_app


LOG = logging.getLogger(__name__)

def config_logging():
    """
    loads configuration for the logging module
    
    The file that is used to load logging configuration is "./log_config.yaml"    
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

def sane_query_args(query_dict):
    """
    checks for the sanity of the paramteres of GET request for /stories
    
    :param query_dict: query parameters
    :type query_dict: dict
    :return: True if sanity check passes, False otherwise
    :rtype: bool
    """

    error_params = dict()

    # limit is a positive integer
    try:
        limit = int(query_dict["limit"])
        if limit <= 0:
            raise ValueError("query paramter (limit) is invalid (non-positive)")   
    except ValueError as err:
        LOG.debug(err)
        error_params.update({"limit": query_dict["limit"]})
    
    # offset must be a non-negative integer
    try:
        offset = int(query_dict["offset"])
        if offset < 0:
            raise ValueError("query parameter (offset) is invalid (negative)")    
    except ValueError as err:
        LOG.debug(err)
        error_params.update({"offset": query_dict["offset"]})

    # sort must be in ["created_at", "updated_at", "title"]
    if query_dict["sort"] not in ["created_at", "updated_at", "title"]:
        error_params.update({"sort": query_dict["sort"]})
    
    # order must be in ["asc", "desc"]
    if query_dict["order"] not in ["asc", "desc"]:
        error_params.update({"order": query_dict["order"]})

    if len(error_params.keys()) == 0:
        return True
    else:
        LOG.error("stories requested with invalid parameter values!")
        LOG.debug(str(error_params))
        return False