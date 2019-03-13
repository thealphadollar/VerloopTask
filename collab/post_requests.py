"""
contains all methods for endpoints that use POST method
"""

import logging
import json

from flask import Blueprint, request, Response


LOG = logging.getLogger(__name__)

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
        words = None
        status_code = 400
        response_dict = dict({"error": "no words detected"})

    if words is not None:
        if len(words) != 1:
            if len(words) == 0:
                resp = "no words sent"
            else:
                resp = "multiple words sent"

            status_code = 400
            response_dict = dict({"error": resp})
        else:
            # TODO: add new word to the dictionary, and return response code
            # 201 if it was new, 200 if old and title and current_sentence.
            db_resp = dict({
                "id": 1,
                "title": "something",
                "created_at": "timestamp",
                "updated_at": "timestamp",
                "body": "something somemore something"
            })

            if db_resp["created_at"] == db_resp["updated_at"]:
                status_code = 201
            else:
                status_code = 200

            body = db_resp["body"]
            cur_para = body[len(body)-1]
            cur_sent = cur_para[len(cur_para)-1]
            response_dict = dict({
                "id": db_resp["id"],
                "title": db_resp["title"],
                "current_sentence": cur_sent
            })

    return Response(
        status = status_code,
        response=json.dumps(response_dict),
        mimetype="application/json"
    )