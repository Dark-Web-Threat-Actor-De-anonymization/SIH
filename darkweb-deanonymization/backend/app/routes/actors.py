from fastapi import APIRouter, HTTPException

from app.crud import fetch_all, fetch_one


router = APIRouter(
    prefix="/actors",
    tags=["Actors"]
)


@router.get("/")
def get_actors():

    actors = fetch_all(
        """
        SELECT
            actor_id,
            name,
            risk_level,
            description,
            created_at
        FROM actors
        ORDER BY actor_id;
        """
    )

    return {
        "actors": actors
    }


@router.get("/{actor_id}")
def get_actor(actor_id: int):

    actor = fetch_one(
        """
        SELECT
            actor_id,
            name,
            risk_level,
            description,
            created_at
        FROM actors
        WHERE actor_id = %s;
        """,
        (actor_id,)
    )

    if not actor:
        raise HTTPException(
            status_code=404,
            detail="Actor/persona not found"
        )

    return {
        "actor": actor
    }