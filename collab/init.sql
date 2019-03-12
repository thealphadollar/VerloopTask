DROP TABLE IF EXISTS stories;

CREATE TABLE stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  /* indexing based on id for easy retrieval */
    created_at TEXT NOT NULL,  /* stores time as string */
    last_modified TEXT,  /* stores time as string */, 
    modifying TEXT NOT NULL,  /* stores "no", "title", "body" */
    title TEXT NOT NULL,
    body TEXT  /* will store stringified JSON */
)

-- default last_modified to created_at
CREATE TRIGGER created_to_last_modified
AFTER INSERT ON stories
FOR EACH ROW
WHEN NEW.last_modified IS NULL
BEGIN
    UPDATE stories SET last_modified = NEW.created_at WHERE id = NEW.id;
END;