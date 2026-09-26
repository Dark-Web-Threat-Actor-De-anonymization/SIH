import os
import json
import hashlib
from datetime import datetime

import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "safe_corpus.jsonl"
)

SOURCE_NAME = "DarkForums Safe Corpus"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):
    """
    Converts DarkForums date strings into PostgreSQL timestamps.

    Example:
        04-08-23, 07:01 PM
        07-08-23, 01:41 PM

    Returns None when the date cannot be parsed.
    """

    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%m-%d-%y, %I:%M %p",
        "%d-%m-%y, %I:%M %p",
        "%m-%d-%Y, %I:%M %p",
        "%d-%m-%Y, %I:%M %p",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


# ============================================================
# CONTENT HASH
# ============================================================

def generate_hash(content):
    """
    Creates a SHA-256 hash for the post content.
    """

    if not content:
        return None

    return hashlib.sha256(
        str(content).encode("utf-8")
    ).hexdigest()


# ============================================================
# NORMALIZE AUTHOR
# ============================================================

def normalize_author(author):
    """
    Converts author values into a consistent string.

    Example:
        [AUTHOR] -> [AUTHOR]
        None     -> unknown
    """

    if author is None:
        return "unknown"

    author = str(author).strip()

    if not author:
        return "unknown"

    return author


# ============================================================
# GET OR CREATE PLATFORM
# ============================================================

def get_or_create_platform(
    cursor,
    forum_name
):
    """
    Creates the forum platform if it does not already exist.
    """

    platform_name = forum_name or "Unknown Forum"

    cursor.execute(
        """
        SELECT platform_id
        FROM platforms
        WHERE name = %s
        """,
        (platform_name,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO platforms
        (
            name,
            platform_type,
            source
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING platform_id
        """,
        (
            platform_name,
            "Forum",
            SOURCE_NAME
        )
    )

    return cursor.fetchone()[0]


# ============================================================
# GET OR CREATE HANDLE
# ============================================================

def get_or_create_handle(
    cursor,
    username,
    platform_id
):
    """
    Creates a handle for a forum author.

    A handle is NOT considered a real-world identity.
    """

    username = normalize_author(username)

    cursor.execute(
        """
        SELECT handle_id
        FROM handles
        WHERE platform_id = %s
        AND username = %s
        """,
        (
            platform_id,
            username
        )
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO handles
        (
            actor_id,
            platform_id,
            username,
            source
        )
        VALUES
        (
            NULL,
            %s,
            %s,
            %s
        )
        RETURNING handle_id
        """,
        (
            platform_id,
            username,
            SOURCE_NAME
        )
    )

    return cursor.fetchone()[0]


# ============================================================
# INSERT THREAD
# ============================================================

def insert_thread(
    cursor,
    thread
):
    """
    Inserts one DarkForums thread.
    """

    thread_id = str(
        thread.get("thread_id")
    )

    title = thread.get("title")

    category = thread.get("category")

    forum_name = thread.get("forum_name")

    date_posted = parse_date(
        thread.get("date_posted")
    )

    platform_id = get_or_create_platform(
        cursor,
        forum_name
    )

    cursor.execute(
        """
        INSERT INTO threads
        (
            thread_id,
            platform_id,
            title,
            category,
            forum_name,
            created_at,
            source
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (thread_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            category = EXCLUDED.category,
            forum_name = EXCLUDED.forum_name,
            created_at = EXCLUDED.created_at
        """,
        (
            thread_id,
            platform_id,
            title,
            category,
            forum_name,
            date_posted,
            SOURCE_NAME
        )
    )

    return platform_id


# ============================================================
# INSERT POST
# ============================================================

def insert_post(
    cursor,
    thread,
    post,
    platform_id
):
    """
    Inserts a post belonging to a thread.
    """

    post_id = str(
        post.get("post_id")
    )

    thread_id = str(
        thread.get("thread_id")
    )

    username = normalize_author(
        post.get(
            "author",
            thread.get("author")
        )
    )

    post_number = post.get(
        "post_number"
    )

    # Convert "#1" -> 1
    if post_number:
        try:
            post_number = int(
                str(post_number)
                .replace("#", "")
                .strip()
            )
        except ValueError:
            post_number = None

    content = post.get(
        "content",
        ""
    )

    post_date = parse_date(
        post.get(
            "post_date"
        )
    )

    handle_id = get_or_create_handle(
        cursor,
        username,
        platform_id
    )

    content_hash = generate_hash(
        content
    )

    cursor.execute(
        """
        INSERT INTO posts
        (
            post_id,
            thread_id,
            handle_id,
            post_number,
            content,
            created_at,
            source,
            language,
            content_hash
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (post_id)
        DO UPDATE SET
            thread_id = EXCLUDED.thread_id,
            handle_id = EXCLUDED.handle_id,
            post_number = EXCLUDED.post_number,
            content = EXCLUDED.content,
            created_at = EXCLUDED.created_at,
            content_hash = EXCLUDED.content_hash
        """,
        (
            post_id,
            thread_id,
            handle_id,
            post_number,
            content,
            post_date,
            SOURCE_NAME,
            "en",
            content_hash
        )
    )


# ============================================================
# IMPORT DATASET
# ============================================================

def import_dataset():

    if not os.path.exists(DATASET_PATH):

        print(
            f"❌ Dataset not found:\n"
            f"{DATASET_PATH}"
        )

        return

    print("=" * 60)
    print("DARKTRACE INTELLIGENCE")
    print("DarkForums Safe Corpus Import")
    print("=" * 60)

    print(
        f"\n📂 Dataset:"
        f"\n{DATASET_PATH}"
    )

    conn = None
    cursor = None

    thread_count = 0
    post_count = 0
    skipped_count = 0

    try:

        conn = get_connection()
        cursor = conn.cursor()

        print("\n🔗 PostgreSQL connection successful.")

        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1
            ):

                line = line.strip()

                if not line:
                    continue

                try:

                    thread = json.loads(line)

                except json.JSONDecodeError as error:

                    print(
                        f"⚠️ Invalid JSON "
                        f"at line {line_number}: "
                        f"{error}"
                    )

                    skipped_count += 1

                    continue

                try:

                    platform_id = insert_thread(
                        cursor,
                        thread
                    )

                    thread_count += 1

                    posts = thread.get(
                        "posts",
                        []
                    )

                    for post in posts:

                        insert_post(
                            cursor,
                            thread,
                            post,
                            platform_id
                        )

                        post_count += 1

                except Exception as error:

                    print(
                        f"⚠️ Error processing "
                        f"thread at line "
                        f"{line_number}: "
                        f"{error}"
                    )

                    skipped_count += 1

                    conn.rollback()

                    continue

                # Commit periodically
                if thread_count % 500 == 0:

                    conn.commit()

                    print(
                        f"📦 Imported "
                        f"{thread_count} threads "
                        f"and "
                        f"{post_count} posts..."
                    )

        conn.commit()

        print("\n" + "=" * 60)
        print("✅ IMPORT COMPLETED")
        print("=" * 60)

        print(
            f"Threads imported : {thread_count}"
        )

        print(
            f"Posts imported   : {post_count}"
        )

        print(
            f"Skipped records  : {skipped_count}"
        )

    except Exception as error:

        if conn:
            conn.rollback()

        print(
            "\n❌ IMPORT FAILED"
        )

        print(
            f"Error: {error}"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

        print(
            "\n🔒 PostgreSQL connection closed."
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import_dataset()