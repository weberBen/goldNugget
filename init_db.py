import sqlite3

if __name__ == "__main__":
    db = sqlite3.connect('database.db')

    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())

    db.commit()
    db.close()