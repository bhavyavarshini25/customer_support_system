-- SQLite Memory Schema
-- ABC Technologies Customer Support System
-- Task 7: SQLite-based memory

CREATE TABLE IF NOT EXISTS conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,
    role        TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
    message     TEXT    NOT NULL,
    intent      TEXT,
    metadata    TEXT
);

-- Index for fast customer history retrieval
CREATE INDEX IF NOT EXISTS idx_customer_id ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_timestamp   ON conversations(timestamp);
