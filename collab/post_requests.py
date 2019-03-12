"""
contains all methods for endpoints that use POST method
"""

import json

from flask import Blueprint, request, Response

add = Blueprint('add_story', __name__, url_prefix='/add')

@add.route('', methods=["POST"])
def add_story():
    """
    endpoint to accept the incoming word
    
    :return: response to the provided request data
    :rtype: flask.Response
    """

    if request.is_json:
        data = request.get_json()
        words = data["word"]
    elif request.args.get("word", None):
        words = request.args.get("word")
    else:
        return Response(
            status=400,
            response=json.dumps({"error": "no words detected"}),
            mimetype="application/json"
        )

    if len(words) != 1:
        if len(words) == 0:
            resp = "no words sent"
        else:
            resp = "multiple words sent"

        return Response(
            status=400,
            response=json.dumps({"error": resp}),
            mimetype="application/json"
        )