import aiosqlite

from config import DATABASE_PATH


def get_connection():
    return aiosqlite.connect(DATABASE_PATH)