# VerloopTask

A backend system to allow editing story by sending REST http requests.

## Requirements

The API is being developed in Python along with basic SQLite.

The application uses the following third-party libraries:

- Flask [framework for web application]
- Pylint [python linter]
- Gunicorn [Web Server Gateway Interface]
- coloredlogs [improved logging system]
- ruamel-yaml [handles YAML config files]
- pydash [manages datatype handling and merging]

## Env Variables

Following environment variables can be used to control the application:

```bash
VERLOOP_DEBUG=TRUE  # truthy value outputs debug logs
FLASK_ENV='development'  # environment for flask app
FLASK_APP='collab'  # to set the path of the flask app
```

## Running

A dockerised version of the API can be run with the `docker-compose.yml` file provided in the directory.

Install [docker-compose](https://docs.docker.com/compose/install/) and [docker](https://docs.docker.com/install/) and run `docker-compose up` from the project directory.

Follow below steps to run it without docker:

```bash
# install python3
cd /path/to/project
pip install pipenv
pipenv shell --three
pipenv install --dev
export FLASK_APP='collab'
flask run
```

## Other Details

### Schema

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

### Logging

The module produces error logs in two ways: an STDOUT stream and a file stream.

STDOUT: The stream's logging level is INFO, unless `VERLOOP_DEBUG` is set to "TRUE".
FileStream: The logs of DEBUG and above level are saved to `~/collab/collab.logs`

Below is a sample format for the logs:

```
03/14/2019 18:04:38 [collab.db_hanlder] [66] [DEBUG   ] SUCCESS: DB connection closed!
```

### Exception Handling

A robust exception handling and sanity checking has been implemented. There are checks on queries and parameters passed in the request to avoid any halting of the system.

The most extensive exception handling has been implemented for database operations and accordingly it has been handled so the response is generated even in case of errors or at least a `500` status code is returned.

### Datastorage

The stories are stored in the SQLite database, `~/collab/collab.sql`

## Testing

Due to shortage of time, tests have not been written since it would take almost equally the same amount of time as the project to write tests. An example of my testing methods can be found at my [project nephos' testing](https://github.com/thealphadollar/Nephos/tree/master/tests).