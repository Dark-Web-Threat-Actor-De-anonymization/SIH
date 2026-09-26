from fastapi import APIRouter, Query

from app.crud import fetch_all


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get("/")
def search(
    q: str = Query(
        ...,
        min_length=1,
        max_length=200
    )
):

    pattern = f"%{q}%"

    posts = fetch_all(
        """
        SELECT
            p.post_id,
            p.thread_id,
            h.username,
            p.content,
            p.created_at,
            t.title,
            t.category,
            t.forum_name
        FROM posts p

        LEFT JOIN handles h
            ON p.handle_id = h.handle_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE
            p.content ILIKE %s
            OR t.title ILIKE %s
            OR t.category ILIKE %s

        ORDER BY
            p.created_at DESC NULLS LAST

        LIMIT 50;
        """,
        (
            pattern,
            pattern,
            pattern
        )
    )

    personas = fetch_all(
        """
        SELECT
            actor_id,
            name,
            description
        FROM actors
        WHERE
            name ILIKE %s
            OR description ILIKE %s

        ORDER BY actor_id;
        """,
        (
            pattern,
            pattern
        )
    )

    return {
        "query": q,
        "posts": posts,
        "personas": personas
    }