# Secure & Efficient ATM (Python)

- SQLite for storage
- Account numbers **encrypted** at rest using `cryptography.Fernet`
- PINs hashed with PBKDF2-HMAC (SHA-256, 150k iterations)
- Simple CLI with `typer`

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m atm.app genkey
python -m atm.app initdb

# Create an account
python -m atm.app create-account --name "Alice" --pin 1234

# Example usage
python -m atm.app deposit-cmd --account 0000000001 --amount 50
python -m atm.app balance --account 0000000001
```
