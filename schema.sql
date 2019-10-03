
CREATE TABLE item (
    id serial PRIMARY KEY,
    repository text,
    name text,
    item_type text,
    subtype text
);
CREATE UNIQUE INDEX unique_item_idx ON item(repository, item_type, subtype, name);

CREATE TABLE previous_status (
    test int REFERENCES item(id),
    context text,
    status text,
    fingerprint text,
    last_updated timestamp,
    PRIMARY KEY (test, context)
);

CREATE TABLE link (
    effected_item int REFERENCES item(id),
    strength real,
    changed_item int REFERENCES item(id),
    context text,
    last_updated timestamp,
    PRIMARY KEY (context, effected_item, changed_item)
);
