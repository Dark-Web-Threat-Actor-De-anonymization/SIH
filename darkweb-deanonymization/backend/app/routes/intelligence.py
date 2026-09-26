from fastapi import APIRouter, HTTPException

from app.crud import fetch_all, fetch_one


router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"]
)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get("/summary")
def get_summary():

    result = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM threads) AS total_threads,
            (SELECT COUNT(*) FROM posts) AS total_posts,
            (SELECT COUNT(*) FROM handles) AS total_handles,
            (SELECT COUNT(*) FROM platforms) AS total_platforms,
            (
                SELECT COUNT(*)
                FROM actors
                WHERE name LIKE 'Analytical Persona Cluster %'
            ) AS total_personas,
            (
                SELECT COUNT(*)
                FROM persona_relationships
            ) AS total_relationships;
        """
    )

    return {
        "summary": result
    }


# ============================================================
# PERSONAS
# ============================================================

@router.get("/personas")
def get_personas():

    personas = fetch_all(
        """
        SELECT
            a.actor_id,
            a.name,
            a.risk_level,
            a.description,
            pf.total_posts,
            pf.avg_post_length,
            pf.post_frequency,
            pf.avg_sentence_length,
            pf.vocabulary_size,
            pf.punctuation_rate,
            pf.technical_term_rate,
            pf.active_hour_start,
            pf.active_hour_end,
            pf.top_category,
            a.created_at
        FROM actors a
        JOIN persona_features pf
            ON a.actor_id = pf.actor_id
        WHERE a.name LIKE
            'Analytical Persona Cluster %'
        ORDER BY pf.total_posts DESC;
        """
    )

    return {
        "personas": personas
    }


# ============================================================
# PERSONA DETAILS
# ============================================================

@router.get("/personas/{actor_id}")
def get_persona(actor_id: int):

    persona = fetch_one(
        """
        SELECT
            a.actor_id,
            a.name,
            a.risk_level,
            a.description,

            pf.avg_post_length,
            pf.post_frequency,
            pf.avg_sentence_length,
            pf.vocabulary_size,
            pf.punctuation_rate,
            pf.technical_term_rate,
            pf.active_hour_start,
            pf.active_hour_end,
            pf.top_category,
            pf.total_posts,
            pf.calculated_at

        FROM actors a

        JOIN persona_features pf
            ON a.actor_id = pf.actor_id

        WHERE a.actor_id = %s
        AND a.name LIKE
            'Analytical Persona Cluster %';
        """,
        (actor_id,)
    )

    if not persona:
        raise HTTPException(
            status_code=404,
            detail="Analytical persona not found"
        )

    return {
        "persona": persona
    }


# ============================================================
# PERSONA POSTS
# ============================================================

@router.get("/personas/{actor_id}/posts")
def get_persona_posts(actor_id: int):

    posts = fetch_all(
        """
        SELECT
            p.post_id,
            p.thread_id,
            p.post_number,
            p.content,
            p.created_at,
            p.content_hash,
            t.title,
            t.category,
            t.forum_name

        FROM post_cluster_assignments pca

        JOIN behavioral_clusters bc
            ON pca.cluster_id = bc.cluster_id

        JOIN posts p
            ON pca.post_id = p.post_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE bc.actor_id = %s

        ORDER BY p.created_at DESC NULLS LAST;
        """,
        (actor_id,)
    )

    return {
        "actor_id": actor_id,
        "posts": posts
    }


# ============================================================
# RELATIONSHIPS
# ============================================================

@router.get("/relationships")
def get_relationships():

    relationships = fetch_all(
        """
        SELECT
            pr.relationship_id,

            pr.actor_a_id,
            a.name AS persona_a,

            pr.actor_b_id,
            b.name AS persona_b,

            pr.linguistic_score,
            pr.behavioral_score,
            pr.topic_score,
            pr.temporal_score,
            pr.overall_confidence,

            pr.explanation,
            pr.created_at

        FROM persona_relationships pr

        JOIN actors a
            ON pr.actor_a_id = a.actor_id

        JOIN actors b
            ON pr.actor_b_id = b.actor_id

        ORDER BY pr.overall_confidence DESC;
        """
    )

    return {
        "relationships": relationships
    }


# ============================================================
# SINGLE RELATIONSHIP
# ============================================================

@router.get("/relationships/{relationship_id}")
def get_relationship(
    relationship_id: int
):

    relationship = fetch_one(
        """
        SELECT
            pr.relationship_id,

            pr.actor_a_id,
            a.name AS persona_a,

            pr.actor_b_id,
            b.name AS persona_b,

            pr.linguistic_score,
            pr.behavioral_score,
            pr.topic_score,
            pr.temporal_score,
            pr.overall_confidence,

            pr.explanation,
            pr.created_at

        FROM persona_relationships pr

        JOIN actors a
            ON pr.actor_a_id = a.actor_id

        JOIN actors b
            ON pr.actor_b_id = b.actor_id

        WHERE pr.relationship_id = %s;
        """,
        (relationship_id,)
    )

    if not relationship:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found"
        )

    return {
        "relationship": relationship
    }


# ============================================================
# BEHAVIORAL CLUSTERS
# ============================================================

@router.get("/clusters")
def get_clusters():

    clusters = fetch_all(
        """
        SELECT
            bc.cluster_id,
            bc.actor_id,
            bc.cluster_name,
            bc.cluster_size,
            bc.avg_post_length,
            bc.avg_sentence_length,
            bc.vocabulary_size,
            bc.punctuation_rate,
            bc.avg_word_length,
            bc.dominant_category,
            bc.dominant_forum,
            bc.representative_keywords

        FROM behavioral_clusters bc

        ORDER BY bc.cluster_id;
        """
    )

    return {
        "clusters": clusters
    }


# ============================================================
# CLUSTER POSTS
# ============================================================

@router.get("/clusters/{cluster_id}/posts")
def get_cluster_posts(
    cluster_id: int
):

    cluster = fetch_one(
        """
        SELECT
            cluster_id,
            actor_id,
            cluster_name
        FROM behavioral_clusters
        WHERE cluster_id = %s;
        """,
        (cluster_id,)
    )

    if not cluster:
        raise HTTPException(
            status_code=404,
            detail="Cluster not found"
        )

    posts = fetch_all(
        """
        SELECT
            p.post_id,
            p.thread_id,
            p.post_number,
            p.content,
            p.created_at,
            pca.similarity_score,
            t.title,
            t.category,
            t.forum_name

        FROM post_cluster_assignments pca

        JOIN posts p
            ON pca.post_id = p.post_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE pca.cluster_id = %s

        ORDER BY
            pca.similarity_score DESC;
        """,
        (cluster_id,)
    )

    return {
        "cluster": cluster,
        "posts": posts
    }