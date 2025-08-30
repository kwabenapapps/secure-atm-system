from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("bank.db")

def get_conn(path: Path = DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db(path: Path = DB_PATH) -> None:
    conn = get_conn(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            acct_encrypted BLOB NOT NULL UNIQUE,
            pin_hash BLOB NOT NULL,
            salt BLOB NOT NULL,
            balance_cents INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS txns (
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            kind TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            counterparty TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()
