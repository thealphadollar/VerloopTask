"""
contains methods to handle database and adjoining operations
"""

import sqlite3
import logging
import json

from contextlib import contextmanager

from flask import current_app, g

from .exceptions import IDNotFound


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
        LOG.info("initializing database...")
        try:
            with self.connect() as conn:
                with current_app.open_resource('init.sql') as f:
                    conn.executescript(f.read().decode('utf-8'))
            LOG.info("SUCCESS: database initialized!")
        except sqlite3.Error as err:
            LOG.debug(err)
            LOG.fatal("FAILED TO INITIALIZE DATABASE AT %s", current_app.config['DATABASE'])
            exit(1)

    @staticmethod
    @contextmanager
    def connect():
        """
        context manager that yields a connection to the database and closes
        it as soon as the context ends
        """

        if 'db' not in g:
            LOG.debug("initializing DB connection...")
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        
        LOG.debug("SUCCESS: DB connection established!")
        yield g.db
        
        db = g.pop('db', None)

        if db is not None:
            db.close()
            LOG.debug("SUCCESS: DB connection closed!")

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
                print(resp)
        except sqlite3.Error as err:
            LOG.debug(err)
            LOG.error("unable to add word %s to database", word)
            return dict()

        if len(resp) == 0:
            resp = DBHandler.create_new_story(word)
        else:
            # gives only the story on which editing is allowed
            sql_cmd = '''
            UPDATE stories
            SET updated_at = (datetime('now')),
                modifying = ?,
                title = ?,
                paragraphs = ?
            WHERE id = ?
            '''

            entry = resp[0]
            paragraphs = json.loads(entry["paragraphs"])
            modifying = [int(x) for x in entry["modifying"].split('|')]
            print(modifying)
            if int(modifying[MOD_TITLE]):
                entry["title"] = entry["title"] + " " + word
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
                        paragraphs[cur_para_index]["sentences"][cur_sent_index] = cur_sent + (" " if cur_sent!="" else "") + word
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
                        str("|".join(map(str, modifying))),
                        entry["title"],
                        json.dumps(paragraphs),
                        entry["id"]
                    ))
                    conn.commit()
                    cursor.execute("SELECT id, title, created_at, updated_at, paragraphs FROM stories WHERE id={};".format(entry["id"]))
                    resp = [dict(row) for row in cursor.fetchall()]
                    resp = resp[0]

            except sqlite3.Error as err:
                LOG.debug(err)
                LOG.error("unable to retrieve (id=%s) from database", entry["id"])
                return dict()

        if len(resp.keys()):
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
        INSERT INTO stories (title)
        VALUES (?)
        '''
        try:
            with DBHandler.connect()  as conn:
                cursor = conn.cursor()
                cursor.execute(sql_cmd, (word,))
                conn.commit()

                cursor.execute("SELECT id, title, created_at, updated_at, paragraphs FROM stories WHERE modifying!='no';")
                resp = [dict(row) for row in cursor.fetchall()]
                resp = resp[0]
        except sqlite3.Error as err:
            LOG.debug(err)
            LOG.error("failed to add data")
            resp = dict()

        return resp

    @staticmethod
    def get_stories(limit, offset, sort, order):
        """
        fetch list of stories from the database and return
        
        :param limit: number of stories
        :type limit: int
        :param offset: number of top results to be skipped
        :type offset: int
        :param sort: column in ["created_at", "updated_at", "title"]
        :type sort: str 
        :param order: order for sort from ["asc", "desc"]
        :type order: str
        :return: stories in a list as following format
                [
                    {
                        "id": 1,
                        "title": "verloop hiring",
                        "created_at": "2018-12-01T00:00:00Z",
                        "updated_at": "2018-12-01T00:01:00Z",
                    }
                ]
        :rtype: list
        """

        sql_cmd = '''
        SELECT id, title, created_at, updated_at
        FROM stories
        ORDER BY {sort_by} {order}
        LIMIT {limit} OFFSET {offset}
        '''.format(
            sort_by = sort.lower(),
            order = order.upper(),
            limit = int(limit),
            offset = int(offset)
        )

        try:
            with DBHandler.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_cmd)
                results = [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as err:
            LOG.debug(err)
            LOG.error("failed to load stories from database")
            results = dict({})
        return results
    
    @staticmethod
    def get_story(id):
        """
        get story with the given id
        
        :param id: id of the story to fetch
        :type id: int
        :raises IDNotFound: id not present in the database
        :return: story with the given id if it exists in the following format:
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
        :rtype: dict
        """

        sql_cmd = '''
        SELECT id, title, created_at, updated_at, paragraphs
        FROM stories
        WHERE id = ?
        '''
        try:
            with DBHandler.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_cmd, (id,))
                results = [dict(row) for row in cursor.fetchall()]
                results = results[0]
                results["paragraphs"] = json.loads(results["paragraphs"])
        except sqlite3.Error as err:
            LOG.debug(err)
            LOG.error("failed to fetch story (id=%s) from database", id)
            results = dict({})
        
        if len(results) == 0:
            raise IDNotFound(id)
               
        return results
            