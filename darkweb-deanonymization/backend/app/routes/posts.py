from fastapi import APIRouter, HTTPException

from app.crud import fetch_all, fetch_one


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/")
def get_posts(
    limit: int = 50
):

    limit = max(
        1,
        min(limit, 500)
    )

    posts = fetch_all(
        f"""
        SELECT
            p.post_id,
            p.thread_id,
            p.handle_id,
            h.username,
            p.post_number,
            p.content,
            p.created_at,
            p.source,
            p.language,
            t.title,
            t.category,
            t.forum_name
        FROM posts p

        LEFT JOIN handles h
            ON p.handle_id = h.handle_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        ORDER BY
            p.created_at DESC NULLS LAST

        LIMIT {limit};
        """
    )

    return {
        "posts": posts,
        "count": len(posts)
    }


@router.get("/{post_id}")
def get_post(post_id: str):

    post = fetch_one(
        """
        SELECT
            p.post_id,
            p.thread_id,
            p.handle_id,
            h.username,
            p.post_number,
            p.content,
            p.created_at,
            p.source,
            p.language,
            p.content_hash,
            t.title,
            t.category,
            t.forum_name
        FROM posts p

        LEFT JOIN handles h
            ON p.handle_id = h.handle_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE p.post_id = %s;
        """,
        (post_id,)
    )

    if not post:

        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return {
        "post": post
    }