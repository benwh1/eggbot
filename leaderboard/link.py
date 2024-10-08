from database import db

key = "leaderboard/linked_accounts"
if key not in db:
    db[key] = {}

def linked_accounts():
    return db[key]

def store_linked_accounts(accounts):
    db[key] = accounts

def link(user_id, lb_username):
    accounts = linked_accounts()
    accounts[user_id] = lb_username
    store_linked_accounts(accounts)

def unlink(user_id):
    accounts = linked_accounts()
    if user_id in accounts:
        del accounts[user_id]
        store_linked_accounts(accounts)

def get_leaderboard_user(user_id):
    accounts = linked_accounts()
    if user_id in accounts:
        return accounts[user_id]
    raise ValueError("user has no linked account")

def get_discord_user(lb_username):
    accounts = linked_accounts()
    for user_id, lb_user in accounts.items():
        if lb_user == lb_username:
            return user_id
    raise ValueError("user has no linked account")
