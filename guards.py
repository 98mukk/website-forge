"""The Gatekeeper: daily build cap so the Forge never burns the wallet."""
import db

MAX_BUILDS_PER_DAY = 25

def allowed():
    return db.builds_today() < MAX_BUILDS_PER_DAY
