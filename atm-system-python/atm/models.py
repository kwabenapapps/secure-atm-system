from __future__ import annotations
import os, hmac, hashlib, secrets
from .storage import get_conn
from .crypto import get_cipher

PBKDF_ITER = 150_000

def _hash_pin(pin: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, PBKDF_ITER)

def create_account(name: str, pin: str, account_number: str | None = None) -> str:
    if not account_number:
        account_number = str(secrets.randbelow(10**10)).zfill(10)
    salt = os.urandom(16)
    pin_hash = _hash_pin(pin, salt)
    cipher = get_cipher()
    acct_enc = cipher.encrypt(account_number.encode())

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO accounts (name, acct_encrypted, pin_hash, salt, balance_cents) VALUES (?,?,?,?,0)",
        (name, acct_enc, pin_hash, salt),
    )
    conn.commit()
    conn.close()
    return account_number

def _get_account_by_number(acct_number: str):
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("SELECT id, name, acct_encrypted, pin_hash, salt, balance_cents FROM accounts").fetchall()
    cipher = get_cipher()
    for r in rows:
        dec = cipher.decrypt(r[2]).decode()
        if dec == acct_number:
            conn.close()
            return r
    conn.close()
    return None

def authenticate(acct_number: str, pin: str):
    row = _get_account_by_number(acct_number)
    if not row:
        return None
    _, _, _, pin_hash, salt, _ = row
    if hmac.compare_digest(pin_hash, _hash_pin(pin, salt)):
        return row[0]  # account_id
    return None

def get_balance(acct_number: str) -> int:
    row = _get_account_by_number(acct_number)
    if not row:
        raise ValueError("Account not found")
    return int(row[5])

def _record_txn(conn, account_id: int, kind: str, amount: int, counterparty: str | None = None):
    conn.execute("INSERT INTO txns (account_id, kind, amount_cents, counterparty) VALUES (?,?,?,?)",
                 (account_id, kind, amount, counterparty))

def deposit(acct_number: str, amount_cents: int):
    if amount_cents <= 0: raise ValueError("amount must be positive")
    row = _get_account_by_number(acct_number)
    if not row: raise ValueError("Account not found")
    account_id = row[0]
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance_cents = balance_cents + ? WHERE id = ?", (amount_cents, account_id))
    _record_txn(cur, account_id, "deposit", amount_cents)
    conn.commit(); conn.close()

def withdraw(acct_number: str, amount_cents: int):
    if amount_cents <= 0: raise ValueError("amount must be positive")
    row = _get_account_by_number(acct_number)
    if not row: raise ValueError("Account not found")
    account_id, _, _, _, _, bal = row
    if bal < amount_cents: raise ValueError("insufficient funds")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE id = ?", (amount_cents, account_id))
    _record_txn(cur, account_id, "withdraw", amount_cents)
    conn.commit(); conn.close()

def transfer(from_acct: str, to_acct: str, amount_cents: int):
    if amount_cents <= 0: raise ValueError("amount must be positive")
    src = _get_account_by_number(from_acct)
    dst = _get_account_by_number(to_acct)
    if not src or not dst: raise ValueError("account not found")
    if src[5] < amount_cents: raise ValueError("insufficient funds")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance_cents = balance_cents - ? WHERE id = ?", (amount_cents, src[0]))
    _record_txn(cur, src[0], "transfer_out", amount_cents, counterparty=to_acct)
    cur.execute("UPDATE accounts SET balance_cents = balance_cents + ? WHERE id = ?", (amount_cents, dst[0]))
    _record_txn(cur, dst[0], "transfer_in", amount_cents, counterparty=from_acct)
    conn.commit(); conn.close()

def history(acct_number: str, limit: int = 20):
    row = _get_account_by_number(acct_number)
    if not row: raise ValueError("Account not found")
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("SELECT kind, amount_cents, counterparty, created_at FROM txns WHERE account_id=? ORDER BY id DESC LIMIT ?",
                       (row[0], limit)).fetchall()
    conn.close()
    return rows
