CREATE TABLE opportunities (
    name TEXT NOT NULL,
    url TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    tag TEXT
);

CREATE TABLE users_opportunities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP,
    details TEXT,
    tag TEXT,
    email TEXT NOT NULL,
    status TEXT
);


create table users(
  emailid TEXT PRIMARY KEY
);


create table admin (
  email text primary key,
  password text
);