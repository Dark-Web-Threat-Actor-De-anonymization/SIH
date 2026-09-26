from fastapi import APIRouter, HTTPException

from app.crud import fetch_all, fetch_one


router = APIRouter(
    prefix="/actor",
    tags=["Profile"]
)


@router.get("/{actor_id}")
def get_profile(actor_id: int):

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
            detail="Persona not found"
        )

    features = fetch_one(
        """
        SELECT
            avg_post_length,
            post_frequency,
            avg_sentence_length,
            vocabulary_size,
            punctuation_rate,
            technical_term_rate,
            active_hour_start,
            active_hour_end,
            top_category,
            total_posts,
            calculated_at
        FROM persona_features
        WHERE actor_id = %s;
        """,
        (actor_id,)
    )

    posts = fetch_all(
        """
        SELECT
            p.post_id,
            p.thread_id,
            p.content,
            p.created_at,
            t.title,
            t.category
        FROM post_cluster_assignments pca

        JOIN behavioral_clusters bc
            ON pca.cluster_id = bc.cluster_id

        JOIN posts p
            ON pca.post_id = p.post_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE bc.actor_id = %s

        ORDER BY p.created_at DESC NULLS LAST

        LIMIT 100;
        """,
        (actor_id,)
    )

    relationships = fetch_all(
        """
        SELECT
            pr.relationship_id,
            pr.actor_a_id,
            pr.actor_b_id,
            pr.linguistic_score,
            pr.behavioral_score,
            pr.topic_score,
            pr.temporal_score,
            pr.overall_confidence,
            pr.explanation
        FROM persona_relationships pr

        WHERE
            pr.actor_a_id = %s
            OR
            pr.actor_b_id = %s

        ORDER BY
            pr.overall_confidence DESC;
        """,
        (
            actor_id,
            actor_id
        )
    )

    return {
        "persona": actor,
        "features": features,
        "posts": posts,
        "relationships": relationships
    }