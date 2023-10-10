import os
from database import db

owner_id = int(os.environ["owner"])

def is_owner(user):
    return user.id == owner_id

def is_egg_admin(user):
    key = "permissions/egg_admin"

    if key not in db:
        db[key] = [owner_id]

    admins = db[key]
    return user.id in admins

def is_egg_moderator(user):
    key = "permissions/egg_moderator"

    if key not in db:
        db[key] = [owner_id]

    moderators = db[key]
    return user.id in moderators
