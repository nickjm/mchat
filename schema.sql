DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS messages;
CREATE TABLE users (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  username    TEXT NOT NULL UNIQUE,
  password    TEXT
);
CREATE TABLE messages (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  sender      TEXT NOT NULL,
  recipient   TEXT NOT NULL,
  media       TEXT NOT NULL,
  metadata    TEXT,
  body        TEXT,
  date_time   DATETIME NOT NULL
);
