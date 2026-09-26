import psycopg2

from app.config import (
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
)


def get_connection():
    """
    Create a PostgreSQL connection.

    Database credentials are loaded from .env
    through app.config.
    """

    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD is missing. "
            "Check the .env file."
        )

    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
    )