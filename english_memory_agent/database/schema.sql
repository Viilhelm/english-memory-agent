-- SQLite schema for English Memory Agent cards table

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_type TEXT NOT NULL,           -- 'error_card', 'rewrite_card', 'expression_card', or 'word_card'
    original_input TEXT NOT NULL,
    corrected_version TEXT,
    natural_version TEXT,
    ielts_version TEXT,                 -- LEGACY: retired 2026-07; kept for backward compat with old rows
    formal_version TEXT,
    chinese_explanation TEXT,
    key_expression TEXT,
    error_type TEXT,
    scenario TEXT,
    tags TEXT,                          -- comma-separated strings
    part_of_speech TEXT,                -- e.g. 'noun', 'verb', 'abbreviation'; used by word_card
    definition TEXT,                    -- English definition; used by word_card
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
