DROP TABLE IF EXISTS notes;
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note_date DATE NOT NULL DEFAULT CURRENT_DATE,
    note_content TEXT NOT NULL,
    note_like_reactions INTEGER NOT NULL DEFAULT 0,
    note_fake_reactions INTEGER NOT NULL DEFAULT 0,
    note_dislike_reactions INTEGER NOT NULL DEFAULT 0,
    deleted INTEGER NOT NULL DEFAULT 0
);

DROP TABLE IF EXISTS notes_users;
CREATE TABLE notes_users (
    id_user INTEGER NOT NULL,
    id_note INTEGER NOT NULL
);
CREATE UNIQUE INDEX note_user_id_unique_index ON notes_users (id_note, id_user);
CREATE INDEX note_user_id_user_index ON notes_users (id_user);
CREATE INDEX note_user_id_note_index ON notes_users (id_user);


DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    api_key CHARACTER(64) NOT NULL,
    deleted INTEGER NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX user_email_unique_index ON users (email);
CREATE UNIQUE INDEX user_api_key_unique_index ON users (api_key);
