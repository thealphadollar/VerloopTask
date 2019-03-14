# VerloopTask

A REST API as a task under Verloop Interview

## Requirements

The API is being developed in Python along with basic SQL.

The application uses the following third-party libraries:

- Flask [framework for web application]
- Pylint [python linter]
- Gunicorn [Web Server Gateway Interface]
- coloredlogs [improved logging system]
- ruamel-yaml [handles YAML config files]
- pydash [manages datatype handling and merging]

## Schema

The database used here is SQLite for the ease of development. Any SQL database can be easily swapped for.

The database has a single table based on the following schema:

```text
id INTEGER PRIMARY KEY AUTOINCREMENT  /* indexing based on id for easy retrieval */
created_at TEXT NOT NULL  /* stores time as string */
last_modified TEXT  /* stores time as string */, 
modifying TEXT NOT NULL  /* stores "no", "title", "paragraphs" */
title TEXT NOT NULL
paragraphs TEXT  /* will store stringified JSON */
```

## Logging

The module produces error logs in two ways: an STDOUT stream and a file stream.

STDOUT: The stream's logging level is INFO, unless `VERLOOP_DEBUG` is set to "TRUE".
FileStream: The logs of DEBUG and above level are saved to `~/collab/collab.logs`

## Datastorage

The stories are stored in the SQLite database, `~/collab/collab.sql`