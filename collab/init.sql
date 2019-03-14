CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  /* indexing based on id for easy retrieval */
    created_at TEXT DEFAULT (datetime('now')),  /* stores time as string */
    updated_at TEXT,  /* stores time as string */
    modifying TEXT DEFAULT "1|0|0",  /* stores "no", "title", "paragraphs" */
    title TEXT NOT NULL,
    paragraphs TEXT DEFAULT '[{"sentences":[""]}]' /* will store stringified JSON */
);

-- default updated_at to created_at
CREATE TRIGGER IF NOT EXISTS created_to_updated
AFTER INSERT ON stories
FOR EACH ROW
WHEN NEW.updated_at IS NULL
BEGIN
    UPDATE stories SET updated_at = NEW.created_at WHERE id = NEW.id;
END;

-- make modifying as "no" when it is equal to 0|6|9
CREATE TRIGGER IF NOT EXISTS update_modifying
AFTER UPDATE ON stories
FOR EACH ROW
BEGIN
    UPDATE stories SET modifying = "no" WHERE modifying="0|6|9";
END;