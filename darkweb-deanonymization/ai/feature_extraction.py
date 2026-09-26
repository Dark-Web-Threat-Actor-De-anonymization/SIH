"""
DarkTrace Intelligence
Behavioral + Linguistic Persona Analysis

This module:

1. Loads imported DarkForums posts from PostgreSQL
2. Extracts linguistic and behavioral features
3. Uses TF-IDF + KMeans to discover anonymous behavioral personas
4. Creates analytical persona records in the actors table
5. Stores persona features in persona_features
6. Assigns posts to behavioral clusters
7. Calculates explainable persona-to-persona similarity
8. Stores relationships in persona_relationships

IMPORTANT:
The DarkForums Safe Corpus anonymizes/redacts authors.
Therefore:
    "Analytical Persona Cluster" != real-world identity

These are behavioral clusters for investigative analysis,
not verified identities.
"""

import os
import re
from collections import Counter

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


# ============================================================
# TECHNICAL / CYBER TERMS
# ============================================================

TECHNICAL_TERMS = {
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "database",
    "dump",
    "leak",
    "leaked",
    "breach",
    "exploit",
    "exploitation",
    "vulnerability",
    "payload",
    "malware",
    "ransomware",
    "trojan",
    "botnet",
    "backdoor",
    "shell",
    "webshell",
    "phishing",
    "credential",
    "credentials",
    "password",
    "hash",
    "md5",
    "sha1",
    "sha256",
    "bcrypt",
    "bitcoin",
    "crypto",
    "wallet",
    "tor",
    "onion",
    "proxy",
    "vpn",
    "ddos",
    "xss",
    "csrf",
    "rce",
    "lfi",
    "rfi",
    "rootkit",
    "stealer",
    "rat",
    "keylogger",
    "api",
    "server",
    "website",
    "ftp",
    "ssh",
    "http",
    "https",
    "wordpress",
    "admin",
    "login",
    "telegram",
    "darkweb",
    "darknet",
}


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    """Create PostgreSQL connection from .env."""

    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(text):
    """Normalize whitespace."""

    if text is None:
        return ""

    text = str(text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text):
    """Extract normalized word tokens."""

    return re.findall(
        r"\b[a-zA-Z0-9_'-]+\b",
        text.lower()
    )


def count_words(text):
    return len(tokenize(text))


def count_sentences(text):
    """Simple sentence estimator."""

    if not text:
        return 0

    sentences = re.split(
        r"[.!?]+",
        text
    )

    valid = [
        s for s in sentences
        if s.strip()
    ]

    return max(1, len(valid))


def avg_sentence_length(text):
    """Average words per sentence."""

    words = count_words(text)

    sentences = count_sentences(text)

    if sentences == 0:
        return 0.0

    return words / sentences


def vocabulary_size(text):
    """Unique normalized vocabulary."""

    words = tokenize(text)

    if not words:
        return 0

    return len(set(words))


def punctuation_rate(text):
    """Punctuation characters / all characters."""

    if not text:
        return 0.0

    punctuation = len(
        re.findall(
            r"[^\w\s]",
            text
        )
    )

    return punctuation / max(
        len(text),
        1
    )


def average_word_length(text):
    words = tokenize(text)

    if not words:
        return 0.0

    return sum(
        len(word)
        for word in words
    ) / len(words)


def technical_term_rate(text):
    words = tokenize(text)

    if not words:
        return 0.0

    technical_count = sum(
        1
        for word in words
        if word in TECHNICAL_TERMS
    )

    return technical_count / len(words)


# ============================================================
# POSTGRESQL DATA LOADING
# ============================================================

def load_posts():

    print("\n[1/7] Loading posts from PostgreSQL...")

    conn = get_connection()

    query = """
        SELECT
            p.post_id,
            p.thread_id,
            p.handle_id,
            p.content,
            p.created_at,
            h.username,
            t.title,
            t.category,
            t.forum_name
        FROM posts p

        LEFT JOIN handles h
            ON p.handle_id = h.handle_id

        LEFT JOIN threads t
            ON p.thread_id = t.thread_id

        WHERE p.content IS NOT NULL
          AND TRIM(p.content) <> ''

        ORDER BY p.created_at NULLS LAST;
    """

    try:

        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            "post_id",
            "thread_id",
            "handle_id",
            "content",
            "created_at",
            "username",
            "title",
            "category",
            "forum_name",
        ]

        df = pd.DataFrame(
            rows,
            columns=columns
        )

        return df

    finally:

        conn.close()


# ============================================================
# ANALYSIS TABLES
# ============================================================

def create_analysis_tables():

    print("\n[2/7] Preparing analysis tables...")

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # Behavioral clusters
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS behavioral_clusters (

                cluster_id SERIAL PRIMARY KEY,

                cluster_name TEXT NOT NULL,

                cluster_size INT DEFAULT 0,

                avg_post_length FLOAT,

                avg_sentence_length FLOAT,

                vocabulary_size FLOAT,

                punctuation_rate FLOAT,

                avg_word_length FLOAT,

                dominant_category TEXT,

                dominant_forum TEXT,

                representative_keywords TEXT,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Add actor/persona mapping to cluster table

        cursor.execute(
            """
            ALTER TABLE behavioral_clusters
            ADD COLUMN IF NOT EXISTS actor_id INT
            REFERENCES actors(actor_id)
            ON DELETE CASCADE;
            """
        )

        # ----------------------------------------------------
        # Post cluster assignments
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            post_cluster_assignments (

                assignment_id SERIAL PRIMARY KEY,

                post_id TEXT UNIQUE
                    REFERENCES posts(post_id)
                    ON DELETE CASCADE,

                cluster_id INT
                    REFERENCES behavioral_clusters(cluster_id)
                    ON DELETE CASCADE,

                similarity_score FLOAT,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        conn.commit()

        print("      Analysis tables ready.")

    finally:

        conn.close()


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_features(df):

    print(
        "\n[3/7] Extracting linguistic "
        "and behavioral features..."
    )

    rows = []

    for _, post in df.iterrows():

        text = clean_text(
            post["content"]
        )

        words = count_words(text)

        sentences = count_sentences(text)

        rows.append(
            {
                "post_id": post["post_id"],
                "thread_id": post["thread_id"],
                "text": text,

                "word_count": words,

                "post_length": words,

                "avg_sentence_length":
                    avg_sentence_length(text),

                "vocabulary_size":
                    vocabulary_size(text),

                "punctuation_rate":
                    punctuation_rate(text),

                "avg_word_length":
                    average_word_length(text),

                "technical_term_rate":
                    technical_term_rate(text),

                "created_at":
                    post["created_at"],

                "category":
                    post["category"]
                    if pd.notna(post["category"])
                    else "Unknown",

                "forum_name":
                    post["forum_name"]
                    if pd.notna(post["forum_name"])
                    else "Unknown",

                "username":
                    post["username"]
                    if pd.notna(post["username"])
                    else "unknown",
            }
        )

    feature_df = pd.DataFrame(rows)

    print(
        f"      Posts analyzed: "
        f"{len(feature_df)}"
    )

    print(
        f"      Average words/post: "
        f"{feature_df['post_length'].mean():.2f}"
    )

    print(
        f"      Average vocabulary: "
        f"{feature_df['vocabulary_size'].mean():.2f}"
    )

    print(
        f"      Average technical-term rate: "
        f"{feature_df['technical_term_rate'].mean():.4f}"
    )

    return feature_df


# ============================================================
# CLUSTER COUNT
# ============================================================

def determine_cluster_count(post_count):

    if post_count < 10:
        return 1

    if post_count < 30:
        return 2

    if post_count < 80:
        return 3

    if post_count < 150:
        return 4

    return 5


# ============================================================
# TOP KEYWORDS
# ============================================================

def get_top_keywords(
    texts,
    max_features=100
):

    if not texts:
        return []

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=max_features,
            min_df=1
        )

        matrix = vectorizer.fit_transform(
            texts
        )

        scores = np.asarray(
            matrix.mean(axis=0)
        ).ravel()

        terms = (
            vectorizer
            .get_feature_names_out()
        )

        indices = (
            scores.argsort()[-10:][::-1]
        )

        return [
            terms[index]
            for index in indices
        ]

    except Exception:

        return []


# ============================================================
# RESET ONLY OUR GENERATED PERSONAS
# ============================================================

def reset_generated_personas():

    print(
        "\n[4/7] Resetting previous "
        "analytical personas..."
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # Relationships involving these personas
        # are removed through ON DELETE CASCADE.

        cursor.execute(
            """
            DELETE FROM actors
            WHERE name LIKE
            'Analytical Persona Cluster %';
            """
        )

        # Remove generated cluster analysis

        cursor.execute(
            """
            DELETE FROM post_cluster_assignments;
            """
        )

        cursor.execute(
            """
            DELETE FROM behavioral_clusters;
            """
        )

        conn.commit()

        print(
            "      Previous analytical results cleared."
        )

    finally:

        conn.close()


# ============================================================
# NORMALIZED SIMILARITY
# ============================================================

def numeric_similarity(
    a,
    b,
    minimum_scale=1.0
):

    if a is None or b is None:

        return 0.0

    try:

        a = float(a)
        b = float(b)

    except (
        TypeError,
        ValueError
    ):

        return 0.0

    denominator = max(
        abs(a),
        abs(b),
        minimum_scale
    )

    score = 1.0 - (
        abs(a - b) /
        denominator
    )

    return float(
        max(
            0.0,
            min(
                1.0,
                score
            )
        )
    )


# ============================================================
# CREATE CLUSTERS + PERSONA FEATURES
# ============================================================

def create_personas(
    feature_df
):

    print(
        "\n[5/7] Discovering behavioral personas..."
    )

    texts = feature_df[
        "text"
    ].tolist()

    if not texts:

        raise ValueError(
            "No text available for clustering."
        )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=1500,
        min_df=1
    )

    tfidf_matrix = vectorizer.fit_transform(
        texts
    )

    cluster_count = determine_cluster_count(
        len(feature_df)
    )

    cluster_count = min(
        cluster_count,
        len(feature_df)
    )

    if cluster_count <= 1:

        labels = np.zeros(
            len(feature_df),
            dtype=int
        )

        model = None

    else:

        model = KMeans(
            n_clusters=cluster_count,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(
            tfidf_matrix
        )

    feature_df[
        "cluster_id"
    ] = labels

    conn = get_connection()

    cluster_map = {}

    try:

        cursor = conn.cursor()

        for cluster_number in sorted(
            feature_df["cluster_id"].unique()
        ):

            cluster_posts = feature_df[
                feature_df["cluster_id"]
                == cluster_number
            ].copy()

            cluster_size = len(
                cluster_posts
            )

            cluster_texts = (
                cluster_posts["text"]
                .tolist()
            )

            # ------------------------------------------------
            # Cluster linguistic statistics
            # ------------------------------------------------

            avg_post_length = (
                cluster_posts["post_length"]
                .mean()
            )

            avg_sentence_length = (
                cluster_posts[
                    "avg_sentence_length"
                ].mean()
            )

            vocabulary = (
                len(
                    set(
                        token
                        for text in cluster_texts
                        for token in tokenize(text)
                    )
                )
            )

            punctuation = (
                cluster_posts[
                    "punctuation_rate"
                ].mean()
            )

            avg_word_len = (
                cluster_posts[
                    "avg_word_length"
                ].mean()
            )

            technical_rate = (
                cluster_posts[
                    "technical_term_rate"
                ].mean()
            )

            # ------------------------------------------------
            # Posting frequency
            # ------------------------------------------------

            dates = pd.to_datetime(
                cluster_posts["created_at"],
                errors="coerce"
            ).dropna()

            if len(dates) >= 2:

                observed_days = (
                    dates.max() -
                    dates.min()
                ).total_seconds() / 86400

                observed_days = max(
                    observed_days,
                    1.0
                )

                post_frequency = (
                    cluster_size /
                    observed_days
                )

            else:

                post_frequency = float(
                    cluster_size
                )

            # ------------------------------------------------
            # Active hours
            # ------------------------------------------------

            hours = (
                dates.dt.hour
                if not dates.empty
                else pd.Series(dtype=float)
            )

            if not hours.empty:

                active_start = int(
                    hours.min()
                )

                active_end = int(
                    hours.max()
                )

            else:

                active_start = None
                active_end = None

            # ------------------------------------------------
            # Category
            # ------------------------------------------------

            category_counts = (
                cluster_posts[
                    "category"
                ]
                .fillna("Unknown")
                .value_counts()
            )

            dominant_category = (
                category_counts.index[0]
                if len(category_counts)
                else "Unknown"
            )

            # ------------------------------------------------
            # Forum
            # ------------------------------------------------

            forum_counts = (
                cluster_posts[
                    "forum_name"
                ]
                .fillna("Unknown")
                .value_counts()
            )

            dominant_forum = (
                forum_counts.index[0]
                if len(forum_counts)
                else "Unknown"
            )

            # ------------------------------------------------
            # Keywords
            # ------------------------------------------------

            keywords = get_top_keywords(
                cluster_texts
            )

            keyword_text = ", ".join(
                keywords
            )

            # ------------------------------------------------
            # Create analytical actor/persona
            # ------------------------------------------------

            actor_name = (
                f"Analytical Persona Cluster "
                f"{cluster_number + 1}"
            )

            description = (
                "Anonymous behavioral persona generated "
                "from DarkForums Safe Corpus posts using "
                "TF-IDF/KMeans analysis. "
                "This label is analytical only and does "
                "not represent a verified real-world identity."
            )

            cursor.execute(
                """
                INSERT INTO actors
                (
                    name,
                    risk_level,
                    description
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                RETURNING actor_id;
                """,
                (
                    actor_name,
                    "Unrated",
                    description
                )
            )

            actor_id = (
                cursor.fetchone()[0]
            )

            # ------------------------------------------------
            # Save persona_features
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO persona_features
                (
                    actor_id,
                    avg_post_length,
                    post_frequency,
                    avg_sentence_length,
                    vocabulary_size,
                    punctuation_rate,
                    technical_term_rate,
                    active_hour_start,
                    active_hour_end,
                    top_category,
                    total_posts
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (actor_id)
                DO UPDATE SET

                    avg_post_length =
                        EXCLUDED.avg_post_length,

                    post_frequency =
                        EXCLUDED.post_frequency,

                    avg_sentence_length =
                        EXCLUDED.avg_sentence_length,

                    vocabulary_size =
                        EXCLUDED.vocabulary_size,

                    punctuation_rate =
                        EXCLUDED.punctuation_rate,

                    technical_term_rate =
                        EXCLUDED.technical_term_rate,

                    active_hour_start =
                        EXCLUDED.active_hour_start,

                    active_hour_end =
                        EXCLUDED.active_hour_end,

                    top_category =
                        EXCLUDED.top_category,

                    total_posts =
                        EXCLUDED.total_posts;
                """,
                (
                    actor_id,
                    float(avg_post_length),
                    float(post_frequency),
                    float(avg_sentence_length),
                    int(vocabulary),
                    float(punctuation),
                    float(technical_rate),
                    active_start,
                    active_end,
                    dominant_category,
                    cluster_size
                )
            )

            # ------------------------------------------------
            # Save behavioral cluster
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO behavioral_clusters
                (
                    cluster_name,
                    cluster_size,
                    avg_post_length,
                    avg_sentence_length,
                    vocabulary_size,
                    punctuation_rate,
                    avg_word_length,
                    dominant_category,
                    dominant_forum,
                    representative_keywords,
                    actor_id
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                RETURNING cluster_id;
                """,
                (
                    actor_name,
                    cluster_size,
                    float(avg_post_length),
                    float(avg_sentence_length),
                    float(vocabulary),
                    float(punctuation),
                    float(avg_word_len),
                    dominant_category,
                    dominant_forum,
                    keyword_text,
                    actor_id
                )
            )

            cluster_db_id = (
                cursor.fetchone()[0]
            )

            cluster_map[
                cluster_number
            ] = {
                "actor_id": actor_id,
                "cluster_db_id": cluster_db_id,
                "keywords": set(keywords),
                "texts": cluster_texts,
            }

            # ------------------------------------------------
            # Assign posts
            # ------------------------------------------------

            cluster_indices = (
                feature_df.index[
                    feature_df["cluster_id"]
                    == cluster_number
                ]
            )

            for df_index in cluster_indices:

                post_id = str(
                    feature_df.loc[
                        df_index,
                        "post_id"
                    ]
                )

                similarity_score = 1.0

                if model is not None:

                    try:

                        centroid = (
                            model.cluster_centers_[
                                cluster_number
                            ]
                        )

                        post_vector = (
                            tfidf_matrix[
                                df_index
                            ].toarray()[0]
                        )

                        denominator = (
                            np.linalg.norm(
                                post_vector
                            )
                            *
                            np.linalg.norm(
                                centroid
                            )
                        )

                        if denominator > 0:

                            similarity_score = (
                                float(
                                    np.dot(
                                        post_vector,
                                        centroid
                                    ) /
                                    denominator
                                )
                            )

                    except Exception:

                        similarity_score = 0.0

                cursor.execute(
                    """
                    INSERT INTO
                    post_cluster_assignments
                    (
                        post_id,
                        cluster_id,
                        similarity_score
                    )
                    VALUES
                    (%s, %s, %s)

                    ON CONFLICT (post_id)
                    DO UPDATE SET

                        cluster_id =
                            EXCLUDED.cluster_id,

                        similarity_score =
                            EXCLUDED.similarity_score;
                    """,
                    (
                        post_id,
                        cluster_db_id,
                        similarity_score
                    )
                )

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()

    print(
        f"      Behavioral personas created: "
        f"{len(cluster_map)}"
    )

    return (
        feature_df,
        cluster_map
    )


# ============================================================
# TEMPORAL SIMILARITY
# ============================================================

def calculate_temporal_similarity(
    df_a,
    df_b
):

    dates_a = pd.to_datetime(
        df_a["created_at"],
        errors="coerce"
    ).dropna()

    dates_b = pd.to_datetime(
        df_b["created_at"],
        errors="coerce"
    ).dropna()

    if dates_a.empty or dates_b.empty:

        return 0.0

    histogram_a = np.bincount(
        dates_a.dt.hour,
        minlength=24
    ).astype(float)

    histogram_b = np.bincount(
        dates_b.dt.hour,
        minlength=24
    ).astype(float)

    if (
        np.linalg.norm(histogram_a) == 0
        or
        np.linalg.norm(histogram_b) == 0
    ):

        return 0.0

    return float(
        cosine_similarity(
            [histogram_a],
            [histogram_b]
        )[0][0]
    )


# ============================================================
# TOPIC SIMILARITY
# ============================================================

def calculate_topic_similarity(
    df_a,
    df_b,
    keywords_a,
    keywords_b
):

    # Category overlap
    categories_a = (
        df_a["category"]
        .fillna("Unknown")
        .value_counts()
    )

    categories_b = (
        df_b["category"]
        .fillna("Unknown")
        .value_counts()
    )

    all_categories = sorted(
        set(categories_a.index)
        |
        set(categories_b.index)
    )

    vector_a = np.array(
        [
            categories_a.get(
                category,
                0
            )
            for category in all_categories
        ],
        dtype=float
    )

    vector_b = np.array(
        [
            categories_b.get(
                category,
                0
            )
            for category in all_categories
        ],
        dtype=float
    )

    if (
        np.linalg.norm(vector_a) > 0
        and
        np.linalg.norm(vector_b) > 0
    ):

        category_similarity = float(
            cosine_similarity(
                [vector_a],
                [vector_b]
            )[0][0]
        )

    else:

        category_similarity = 0.0

    # Keyword overlap
    union = keywords_a | keywords_b

    if union:

        keyword_similarity = (
            len(
                keywords_a & keywords_b
            )
            /
            len(union)
        )

    else:

        keyword_similarity = 0.0

    return float(
        0.5 * category_similarity
        +
        0.5 * keyword_similarity
    )


# ============================================================
# BEHAVIORAL SIMILARITY
# ============================================================

def calculate_behavioral_similarity(
    feature_a,
    feature_b
):

    similarities = []

    # Count-based features
    similarities.append(
        numeric_similarity(
            feature_a["total_posts"],
            feature_b["total_posts"],
            minimum_scale=1
        )
    )

    similarities.append(
        numeric_similarity(
            feature_a["avg_post_length"],
            feature_b["avg_post_length"],
            minimum_scale=1
        )
    )

    similarities.append(
        numeric_similarity(
            feature_a["avg_sentence_length"],
            feature_b["avg_sentence_length"],
            minimum_scale=1
        )
    )

    similarities.append(
        numeric_similarity(
            feature_a["vocabulary_size"],
            feature_b["vocabulary_size"],
            minimum_scale=1
        )
    )

    # Rate features
    similarities.append(
        numeric_similarity(
            feature_a["punctuation_rate"],
            feature_b["punctuation_rate"],
            minimum_scale=0.001
        )
    )

    similarities.append(
        numeric_similarity(
            feature_a["technical_term_rate"],
            feature_b["technical_term_rate"],
            minimum_scale=0.001
        )
    )

    similarities.append(
        numeric_similarity(
            feature_a["post_frequency"],
            feature_b["post_frequency"],
            minimum_scale=0.001
        )
    )

    return float(
        np.mean(similarities)
    )


# ============================================================
# LINGUISTIC SIMILARITY
# ============================================================

def calculate_linguistic_similarity(
    feature_df,
    cluster_a,
    cluster_b,
    vectorizer,
    matrix
):

    texts_a = feature_df[
        feature_df["cluster_id"]
        == cluster_a
    ]["text"].tolist()

    texts_b = feature_df[
        feature_df["cluster_id"]
        == cluster_b
    ]["text"].tolist()

    if not texts_a or not texts_b:

        return 0.0

    indices_a = feature_df.index[
        feature_df["cluster_id"]
        == cluster_a
    ]

    indices_b = feature_df.index[
        feature_df["cluster_id"]
        == cluster_b
    ]

    centroid_a = np.asarray(
        matrix[
            list(indices_a)
        ].mean(axis=0)
    )

    centroid_b = np.asarray(
        matrix[
            list(indices_b)
        ].mean(axis=0)
    )

    return float(
        cosine_similarity(
            centroid_a,
            centroid_b
        )[0][0]
    )


# ============================================================
# SAVE RELATIONSHIPS
# ============================================================

def create_relationships(
    feature_df,
    cluster_map
):

    print(
        "\n[6/7] Calculating persona relationships..."
    )

    cluster_numbers = sorted(
        cluster_map.keys()
    )

    if len(cluster_numbers) < 2:

        print(
            "      Fewer than two personas available."
        )

        return

    # Re-create global TF-IDF representation

    texts = feature_df[
        "text"
    ].tolist()

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=1500,
        min_df=1
    )

    matrix = vectorizer.fit_transform(
        texts
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # Clear previously generated
        # analytical relationships

        cursor.execute(
            """
            DELETE FROM persona_relationships
            WHERE actor_a_id IN (
                SELECT actor_id
                FROM actors
                WHERE name LIKE
                'Analytical Persona Cluster %'
            )
            OR actor_b_id IN (
                SELECT actor_id
                FROM actors
                WHERE name LIKE
                'Analytical Persona Cluster %'
            );
            """
        )

        for i in range(
            len(cluster_numbers)
        ):

            for j in range(
                i + 1,
                len(cluster_numbers)
            ):

                cluster_a = (
                    cluster_numbers[i]
                )

                cluster_b = (
                    cluster_numbers[j]
                )

                actor_a = cluster_map[
                    cluster_a
                ]["actor_id"]

                actor_b = cluster_map[
                    cluster_b
                ]["actor_id"]

                df_a = feature_df[
                    feature_df["cluster_id"]
                    == cluster_a
                ]

                df_b = feature_df[
                    feature_df["cluster_id"]
                    == cluster_b
                ]

                # --------------------------------------------
                # Linguistic
                # --------------------------------------------

                linguistic = (
                    calculate_linguistic_similarity(
                        feature_df,
                        cluster_a,
                        cluster_b,
                        vectorizer,
                        matrix
                    )
                )

                # --------------------------------------------
                # Extract aggregate features
                # --------------------------------------------

                def aggregate(df):

                    dates = pd.to_datetime(
                        df["created_at"],
                        errors="coerce"
                    ).dropna()

                    if len(dates) >= 2:

                        days = (
                            dates.max()
                            -
                            dates.min()
                        ).total_seconds() / 86400

                        days = max(days, 1)

                        frequency = (
                            len(df) /
                            days
                        )

                    else:

                        frequency = len(df)

                    return {
                        "avg_post_length":
                            df["post_length"].mean(),

                        "avg_sentence_length":
                            df[
                                "avg_sentence_length"
                            ].mean(),

                        "vocabulary_size":
                            df[
                                "vocabulary_size"
                            ].mean(),

                        "punctuation_rate":
                            df[
                                "punctuation_rate"
                            ].mean(),

                        "technical_term_rate":
                            df[
                                "technical_term_rate"
                            ].mean(),

                        "post_frequency":
                            frequency,

                        "total_posts":
                            len(df),
                    }

                feature_a = aggregate(
                    df_a
                )

                feature_b = aggregate(
                    df_b
                )

                # --------------------------------------------
                # Behavioral
                # --------------------------------------------

                behavioral = (
                    calculate_behavioral_similarity(
                        feature_a,
                        feature_b
                    )
                )

                # --------------------------------------------
                # Topic
                # --------------------------------------------

                topic = (
                    calculate_topic_similarity(
                        df_a,
                        df_b,
                        cluster_map[
                            cluster_a
                        ]["keywords"],
                        cluster_map[
                            cluster_b
                        ]["keywords"]
                    )
                )

                # --------------------------------------------
                # Temporal
                # --------------------------------------------

                temporal = (
                    calculate_temporal_similarity(
                        df_a,
                        df_b
                    )
                )

                # --------------------------------------------
                # Overall
                # --------------------------------------------

                overall = (
                    0.40 * linguistic
                    +
                    0.25 * behavioral
                    +
                    0.15 * topic
                    +
                    0.20 * temporal
                )

                # --------------------------------------------
                # Explanation
                # --------------------------------------------

                supporting = []

                if linguistic >= 0.50:

                    supporting.append(
                        "similar language patterns"
                    )

                if behavioral >= 0.50:

                    supporting.append(
                        "similar behavioral statistics"
                    )

                if topic >= 0.50:

                    supporting.append(
                        "overlapping topic signals"
                    )

                if temporal >= 0.50:

                    supporting.append(
                        "similar posting-hour patterns"
                    )

                if supporting:

                    explanation = (
                        "Potential analytical relationship "
                        "supported by "
                        +
                        ", ".join(supporting)
                        +
                        "."
                    )

                else:

                    explanation = (
                        "Limited similarity signals were "
                        "observed across the available "
                        "linguistic, behavioral, topic and "
                        "temporal evidence."
                    )

                explanation += (
                    " This is a similarity signal between "
                    "anonymous behavioral clusters and is "
                    "not proof of common real-world authorship."
                )

                # --------------------------------------------
                # Save
                # --------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO persona_relationships
                    (
                        actor_a_id,
                        actor_b_id,
                        linguistic_score,
                        behavioral_score,
                        topic_score,
                        temporal_score,
                        overall_confidence,
                        explanation
                    )
                    VALUES
                    (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    ON CONFLICT
                    (
                        actor_a_id,
                        actor_b_id
                    )
                    DO UPDATE SET

                        linguistic_score =
                            EXCLUDED.linguistic_score,

                        behavioral_score =
                            EXCLUDED.behavioral_score,

                        topic_score =
                            EXCLUDED.topic_score,

                        temporal_score =
                            EXCLUDED.temporal_score,

                        overall_confidence =
                            EXCLUDED.overall_confidence,

                        explanation =
                            EXCLUDED.explanation;
                    """,
                    (
                        actor_a,
                        actor_b,
                        linguistic,
                        behavioral,
                        topic,
                        temporal,
                        overall,
                        explanation
                    )
                )

        conn.commit()

        print(
            f"      Relationships generated: "
            f"{len(cluster_numbers) * (len(cluster_numbers) - 1) // 2}"
        )

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results():

    print(
        "\n[7/7] Displaying final analytical results..."
    )

    conn = get_connection()

    try:

        cursor = conn.cursor()

        # ----------------------------------------------------
        # Personas
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                a.actor_id,
                a.name,
                pf.total_posts,
                ROUND(
                    pf.avg_post_length::numeric,
                    2
                ),
                ROUND(
                    pf.post_frequency::numeric,
                    4
                ),
                pf.vocabulary_size,
                ROUND(
                    pf.technical_term_rate::numeric,
                    4
                ),
                pf.top_category
            FROM actors a

            JOIN persona_features pf
                ON a.actor_id = pf.actor_id

            WHERE a.name LIKE
                'Analytical Persona Cluster %'

            ORDER BY pf.total_posts DESC;
            """
        )

        personas = cursor.fetchall()

        print("\n" + "=" * 75)
        print("ANALYTICAL PERSONAS")
        print("=" * 75)

        for row in personas:

            print(
                f"\n{row[1]}"
            )

            print(
                f"  Actor/Persona ID : {row[0]}"
            )

            print(
                f"  Posts            : {row[2]}"
            )

            print(
                f"  Avg post words   : {row[3]}"
            )

            print(
                f"  Post frequency   : {row[4]} / day"
            )

            print(
                f"  Vocabulary       : {row[5]}"
            )

            print(
                f"  Technical rate   : {row[6]}"
            )

            print(
                f"  Top category     : {row[7]}"
            )

        # ----------------------------------------------------
        # Relationships
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                a.name,
                b.name,

                ROUND(
                    pr.linguistic_score::numeric,
                    2
                ),

                ROUND(
                    pr.behavioral_score::numeric,
                    2
                ),

                ROUND(
                    pr.topic_score::numeric,
                    2
                ),

                ROUND(
                    pr.temporal_score::numeric,
                    2
                ),

                ROUND(
                    pr.overall_confidence::numeric,
                    2
                ),

                pr.explanation

            FROM persona_relationships pr

            JOIN actors a
                ON pr.actor_a_id = a.actor_id

            JOIN actors b
                ON pr.actor_b_id = b.actor_id

            WHERE a.name LIKE
                'Analytical Persona Cluster %'

            ORDER BY
                pr.overall_confidence DESC;
            """
        )

        relationships = (
            cursor.fetchall()
        )

        print("\n" + "=" * 75)
        print("PERSONA RELATIONSHIPS")
        print("=" * 75)

        for row in relationships:

            print(
                f"\n{row[0]} <-> {row[1]}"
            )

            print(
                f"  Linguistic : {row[2]}"
            )

            print(
                f"  Behavioral : {row[3]}"
            )

            print(
                f"  Topic      : {row[4]}"
            )

            print(
                f"  Temporal   : {row[5]}"
            )

            print(
                f"  Confidence : {row[6]}"
            )

            print(
                f"  Explanation: {row[7]}"
            )

    finally:

        conn.close()


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 75)
    print("DARKTRACE INTELLIGENCE")
    print("BEHAVIORAL + LINGUISTIC PERSONA ANALYSIS")
    print("=" * 75)

    try:

        # ----------------------------------------------------
        # Load
        # ----------------------------------------------------

        df = load_posts()

        if df.empty:

            print(
                "\n❌ No posts available."
            )

            return

        print(
            f"      Posts loaded: {len(df)}"
        )

        # ----------------------------------------------------
        # Prepare
        # ----------------------------------------------------

        create_analysis_tables()

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        feature_df = extract_features(
            df
        )

        # ----------------------------------------------------
        # Reset old generated results
        # ----------------------------------------------------

        reset_generated_personas()

        # ----------------------------------------------------
        # Create personas
        # ----------------------------------------------------

        feature_df, cluster_map = (
            create_personas(
                feature_df
            )
        )

        # ----------------------------------------------------
        # Relationships
        # ----------------------------------------------------

        create_relationships(
            feature_df,
            cluster_map
        )

        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        display_results()

        print("\n")
        print("=" * 75)
        print("✅ ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 75)

    except Exception as error:

        print("\n")
        print("=" * 75)
        print("❌ FEATURE EXTRACTION FAILED")
        print("=" * 75)

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()