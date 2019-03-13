DROP TABLE IF EXISTS stories;

CREATE TABLE stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  /* indexing based on id for easy retrieval */
    created_at TEXT NOT NULL,  /* stores time as string */
    updated_at TEXT,  /* stores time as string */, 
    modifying TEXT NOT NULL,  /* stores "no", "title", "body" */
    title TEXT NOT NULL,
    body TEXT  /* will store stringified JSON */
)

-- default last_modified to created_at
CREATE TRIGGER created_to_updates
AFTER INSERT ON stories
FOR EACH ROW
WHEN NEW.updated_at IS NULL
BEGIN
    UPDATE stories SET updated_at = NEW.created_at WHERE id = NEW.id;
END;