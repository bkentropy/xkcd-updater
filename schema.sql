
CREATE TABLE entries(
    id text primary key,
    title text,
    imglink text,
    summary text,
    pubts text,
    posted bool
);

CREATE TABLE lastpub(
    id text primary key
);
