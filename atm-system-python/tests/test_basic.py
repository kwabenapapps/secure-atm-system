from atm.storage import init_db, DB_PATH
from atm.models import create_account, deposit, withdraw, get_balance

def setup_module(module):
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()

def test_deposit_withdraw():
    acct = create_account("Test", "1234", "0000000001")
    deposit(acct, 5000)
    assert get_balance(acct) == 5000
    withdraw(acct, 2000)
    assert get_balance(acct) == 3000
