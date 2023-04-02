import sqlite3
import config

if __name__ == "__main__":
    db = sqlite3.connect(config.DATABASE_PATH)

    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    
    with open('seed.sql', 'r') as f:
        db.cursor().executescript(f.read())

    db.commit()
    db.close()