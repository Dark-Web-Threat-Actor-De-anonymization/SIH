from fastapi import APIRouter, HTTPException

from app.crud import fetch_all, fetch_one


router = APIRouter(
    prefix="/handles",
    tags=["Handles"]
)


@router.get("/")
def get_handles():

    handles = fetch_all(
        """
        SELECT
            h.handle_id,
            h.actor_id,
            h.platform_id,
            h.username,
            h.first_seen,
            h.last_seen,
            h.source,
            p.name AS platform_name
        FROM handles h

        LEFT JOIN platforms p
            ON h.platform_id = p.platform_id

        ORDER BY h.handle_id;
        """
    )

    return {
        "handles": handles
    }


@router.get("/{handle_id}")
def get_handle(handle_id: int):

    handle = fetch_one(
        """
        SELECT
            h.handle_id,
            h.actor_id,
            h.platform_id,
            h.username,
            h.first_seen,
            h.last_seen,
            h.source,
            p.name AS platform_name
        FROM handles h

        LEFT JOIN platforms p
            ON h.platform_id = p.platform_id

        WHERE h.handle_id = %s;
        """,
        (handle_id,)
    )

    if not handle:

        raise HTTPException(
            status_code=404,
            detail="Handle not found"
        )

    return {
        "handle": handle
    }


@router.get("/actor/{actor_id}")
def get_handles_by_actor(actor_id: int):

    handles = fetch_all(
        """
        SELECT
            h.handle_id,
            h.username,
            h.platform_id,
            h.first_seen,
            h.last_seen,
            h.source,
            p.name AS platform_name
        FROM handles h

        LEFT JOIN platforms p
            ON h.platform_id = p.platform_id

        WHERE h.actor_id = %s

        ORDER BY h.handle_id;
        """,
        (actor_id,)
    )

    return {
        "actor_id": actor_id,
        "handles": handles
    }