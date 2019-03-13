"""
contains all methods for endpoints that use GET method
"""

import logging
import json

from flask import Blueprint, request, Response

from .helpers import sane_query_args
from .exceptions import IDNotFound


LOG = logging.getLogger(__name__)
stories = Blueprint('get_story', __name__, url_prefix='/stories')

@stories.route('', methods=["GET"])
def get_story_list():
    """
    endpoint to send list of stories

    The following query parameters are valid:
        limit: uint32 -
        offset: uint32 -
        sort: enum: created_at, updated_at, title
        order: enum: asc, desc

    The response format is as below:
    {
        "limit": 100,
        "offset": 0,
        "count": 1,
        "results":[
            {
                "id": 1,
                "title": "verloop hiring",
                "created_at": "2018-12-01T00:00:00Z",
                "updated_at": "2018-12-01T00:01:00Z",
            }
        ]
    }

    :return: response
    :rtype: flask.Response
    """

    query_dict = dict({
        "limit": request.args.get("limit", 100),
        "offset": request.args.get("offset", 0),
        "sort": request.args.get("sort", "created_at").lower(),
        "order": request.args.get("order", "asc").lower()
    })

    # check for sanity of given input parameters
    sanity_check_resp = sane_query_args(query_dict)
    if len(sanity_check_resp.keys()) != 0:
        status_code = 400
        response_dict = dict({"invalid parameters": sanity_check_resp, "error": "invalid parameter values"})

    else:
        # TODO: implement code for getting list of stories
        results = [
                    {
                        "id": 1,
                        "title": "verloop hiring",
                        "created_at": "2018-12-01T00:00:00Z",
                        "updated_at": "2018-12-01T00:01:00Z",
                    }
                ]
        status_code = 200
        response_dict = dict({
            "limit": query_dict["limit"],
            "offset": query_dict["offset"],
            "count": len(results),
            "results": results
        })

    return Response(
        status = status_code,
        response=json.dumps(response_dict),
        mimetype="application/json"
    )

@stories.route('/<id>')
def get_story(id):
    """
    gets a story from the database provided it's id
    
    :param id: id of the story
    :type id: int
    :return: response
    :rtype: flask.Response
    """
    try:
        # raises ValueError if id is non-integer
        id = int(id)
        # TODO: check if 0 is acceptable
        if id < 0:
            raise ValueError("route parameter (id) is invalid (negative)")
        
        # TODO: query database for the particular story, raise idNotFound Error
        try:
            db_resp = dict(
                {
                    "id": 1,
                    "title": "verloop hiring",
                    "created_at": "2018-12-01T00:00:00Z",
                    "updated_at": "2018-12-01T00:01:00Z",
                    "paragraphs":[
                        {
                            "sentences":[
                                "hi!"
                            ]
                        }
                    ]
                }
            )
        except IDNotFound as err:
            LOG.error(err)
            raise ValueError("route parameter (id) is invalid (not found)")

        status_code = 200
        response_dict = db_resp

    except ValueError as err:
        LOG.error(err)
        LOG.debug(str({"id": id}))
        status_code = 400
        response_dict = dict({"id": id, "error": "invalid id"})

    return Response(
        status=status_code,
        response=json.dumps(response_dict),
        mimetype="application/json"
    )