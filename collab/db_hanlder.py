"""
contains methods to handle database and adjoining operations
"""

import sqlite3
import logging
import json

from contextlib import contextmanager

from flask import current_app, g


LOG = logging.getLogger(__name__)

# index of modifying table
MOD_TITLE = 0
MOD_PARA = 1
MOD_SENT = 2

class DBHandler:
    """
    class encapsulating all database methods
    """
    
    def __init__(self):
        """
        initialises database with instructions in init.sql        
        """

        with self.connect() as conn:
            with current_app.open_resource('init.sql') as f:
                conn.executescript(f.read().decode('utf-8'))

    @staticmethod
    @contextmanager
    def connect():
        """
        context manager that yields a connection to the database and closes
        it as soon as the context ends
        """

        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        
        yield g.db
        
        db = g.pop('db', None)

        if db is not None:
            db.close()

    @staticmethod
    def add_word(word):
        """
        adds a new word to existing story, or calls function to create a new story
        
        :param word: word to be added
        :type word: str
        :return: edited story as dictionary of the following format (with example values)
            {
                "id": 1,
                "title": "something",
                "created_at": "timestamp",
                "updated_at": "timestamp",
                "paragraphs": "lorem potem ipsum"
            }
        :rtype: dict
        """

        try:
            with DBHandler.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, modifying, title, paragraphs FROM stories WHERE modifying != 'no';")
                resp = [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as err:
            LOG.error(err)
            LOG.debug("unable to add word %s to database", word)
            return dict()

        if len(resp) == 0:
            resp = DBHandler.create_new_story(word)
        else:
            # gives only the story on which editing is allowed
            sql_cmd = '''
            UPDATE stories
            SET updated_at = datetime('now')
                modifying = ?,
                title = ?,
                paragraphs = ?
            WHERE id = ?
            '''

            entry = resp[0]
            paragraphs = json.loads(entry["paragraphs"])
            modifying = [map(int, entry["modifying"].split('|'))]

            if modifying[MOD_TITLE]:
                entry["title"] = resp["title"] + " " + word
                modifying[MOD_TITLE] = 0
            else:
                cur_para_index = modifying[MOD_PARA]
                cur_sent_index = modifying[MOD_SENT]
                 
                added = False
                while(not added):
                    try:
                        cur_sent = paragraphs[cur_para_index]["sentences"][cur_sent_index]
                    except IndexError as _:
                        paragraphs[cur_para_index]["sentences"].append("")
                        cur_sent = paragraphs[cur_para_index]["sentences"][cur_sent_index]

                    if len(cur_sent.split()) < 15:
                        paragraphs[cur_para_index]["sentences"][cur_sent_index] = cur_sent + " " + word
                        added = True
                    else:
                        if cur_sent_index < 9:
                            cur_sent_index += 1
                        else:
                            cur_sent_index = 0
                            cur_para_index += 1
                            paragraphs.append(dict({
                                "sentences": []
                            }))
                
                # corner case for changing modifying entry in DB to "0|6|9" before next time to trigger change
                if (cur_para_index==6 and cur_sent_index==8) and len(paragraphs[cur_para_index]["sentences"][cur_sent_index].split()) >= 15:
                    cur_sent_index += 1

                modifying[MOD_PARA] = cur_para_index
                modifying[MOD_SENT] = cur_sent_index

            try:
                with DBHandler.connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql_cmd, (
                        "|".join(map(str, modifying)),
                        entry["title"],
                        json.dumps(paragraphs),
                        entry["id"]
                    ))
                    conn.commit()
                    cursor.execute("SELECT id, title, created_at, updated_at, paragraphs FROM stories WHERE id={};".format(entry["id"]))
                    resp = [dict(row) for row in cursor.fetchall()]
                    resp = resp[0]

            except sqlite3.Error as err:
                LOG.error(err)
                LOG.debug("unable to retrieve (id=%s) from database", entry["id"])
                return dict()

        resp["paragraphs"] = json.loads(resp["paragraphs"])
        return resp
            
    @staticmethod
    def create_new_story(word):
        """
        adds a new story entry in the table
        
        :param word: word to be added
        :type word: str
        :return: added story as dictionary of the following format (with example values)
            {
                "id": 1,
                "title": "something",
                "created_at": "timestamp",
                "updated_at": "timestamp",
                "paragraphs": "lorem potem ipsum"
            }
        :rtype: dict
        """

        sql_cmd = '''
        INSERT INTO stories title
        VALUES ?
        '''
        try:
            with DBHandler.connect()  as conn:
                cursor = conn.cursor()
                cursor.execute(sql_cmd, word)
                conn.commit()

                cursor.execute("SELECT id, title, created_at, updated_at, paragraphs FROM stories WHERE modifying!='no';")
                resp = [dict(row) for row in cursor.fetchall()]
                resp = resp[0]
        except sqlite3.Error as err:
            LOG.error(err)
            LOG.debug("failed to add data")
            resp = dict()

        return resp

    @staticmethod
    def get_stories