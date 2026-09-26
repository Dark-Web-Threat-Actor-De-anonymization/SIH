from typing import Any, Dict, List, Optional

from psycopg2.extras import RealDictCursor

from app.database import get_connection


def fetch_all(
    query: str,
    params: Optional[tuple] = None
) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return all rows as dictionaries.
    """

    conn = get_connection()

    try:
        with conn.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(query, params)

            return [
                dict(row)
                for row in cursor.fetchall()
            ]

    finally:
        conn.close()


def fetch_one(
    query: str,
    params: Optional[tuple] = None
) -> Optional[Dict[str, Any]]:
    """
    Execute a SELECT query and return one row.
    """

    conn = get_connection()

    try:
        with conn.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            cursor.execute(query, params)

            row = cursor.fetchone()

            return dict(row) if row else None

    finally:
        conn.close()


def execute_query(
    query: str,
    params: Optional[tuple] = None
) -> None:
    """
    Execute a write query and commit.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                query,
                params
            )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:
        conn.close()