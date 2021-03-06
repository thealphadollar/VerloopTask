"""
contains all methods for endpoints that use POST method
"""

import logging
import json

from flask import Blueprint, request, Response

from .db_hanlder import DBHandler

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
        LOG.warning("No data added: no 'word' data received in the request")

    if words is not None:
        if len(words.split()) != 1:
            if len(words) == 0:
                resp = "no words sent"
                LOG.warning("No data added: no words detected in request!")
            else:
                resp = "multiple words sent"
                LOG.warning("No data added: multiple words (%s) detected in request!", words)

            status_code = 400
            response_dict = dict({"error": resp})
        else:

            LOG.info("Adding word (%s) to the stories table", words)

            db_resp = DBHandler.add_word(words)

            # return internal server error in case of Database Error
            if len(db_resp.keys()) == 0:
                LOG.error("FAILED: adding word (%s) to the stories table", words)
                return Response(status=500)

            if db_resp["created_at"] == db_resp["updated_at"]:
                LOG.info("SUCCESS: new story start with word (%s)", words)
                status_code = 201
            else:
                LOG.info("SUCCESS: story updated with word (%s)", words)
                status_code = 200

            paragraphs = db_resp["paragraphs"]
            cur_para = paragraphs[len(paragraphs)-1]["sentences"]
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