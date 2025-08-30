from __future__ import annotations
import typer
from typing import Optional
from .storage import init_db
from .models import create_account, authenticate, get_balance, deposit, withdraw, transfer, history
from .crypto import generate_key

app = typer.Typer(add_completion=False, help="Secure ATM CLI (SQLite + encrypted account numbers).")

@app.command()
def initdb():
    init_db()
    typer.echo("Database initialized.")

@app.command()
def genkey():
    generate_key()
    typer.echo("Key generated at atm/secret.key")

@app.command("create-account")
def create_account_cmd(name: str = typer.Option(..., help="Customer name"),
                       pin: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
                       account_number: Optional[str] = typer.Option(None, help="Optional 10-digit number (auto if omitted)")):
    acct = create_account(name, pin, account_number)
    typer.echo(f"✅ Account created.\nRecord this number securely: {acct}\n")

@app.command()
def login(account: str = typer.Option(..., help="10-digit account number"),
          pin: str = typer.Option(..., prompt=True, hide_input=True)):
    if authenticate(account, pin):
        typer.echo("Login successful.")
    else:
        raise typer.Exit(code=1)

@app.command()
def balance(account: str):
    cents = get_balance(account)
    typer.echo(f"Balance: ${cents/100:.2f}")

@app.command(name="deposit-cmd")
def deposit_cmd(account: str, amount: float):
    deposit(account, int(round(amount * 100)))
    typer.echo(f"Deposited ${amount:.2f}")

@app.command(name="withdraw-cmd")
def withdraw_cmd(account: str, amount: float):
    withdraw(account, int(round(amount * 100)))
    typer.echo(f"Withdrew ${amount:.2f}")

@app.command(name="transfer-cmd")
def transfer_cmd(from_account: str, to_account: str, amount: float):
    transfer(from_account, to_account, int(round(amount * 100)))
    typer.echo(f"Transferred ${amount:.2f} from {from_account} to {to_account}")

@app.command(name="history-cmd")
def history_cmd(account: str, limit: int = 10):
    for k, amt, cp, ts in history(account, limit):
        typer.echo(f"[{ts}] {k:<13} ${amt/100:.2f} {('(' + str(cp) + ')') if cp else ''}")

if __name__ == "__main__":
    app()
