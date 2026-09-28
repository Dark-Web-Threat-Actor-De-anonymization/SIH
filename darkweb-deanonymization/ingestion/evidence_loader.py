import csv
import os

import psycopg2
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

EVIDENCE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "evidence.csv",
)


SOURCE_NAME = "DarkTrace Evidence CSV"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


# ============================================================
# EVIDENCE TYPE MAPPING
# ============================================================

def determine_evidence_type(
    description: str,
) -> str:
    """
    Map the known evidence descriptions in the
    supplied CSV to a stable evidence type.

    Unknown descriptions use LEGACY rather than
    silently inventing a specific classification.
    """

    text = (
        str(description)
        .strip()
        .lower()
    )

    if "language" in text:
        return "LINGUISTIC"

    if "wallet" in text:
        return "WALLET"

    if "handle" in text:
        return "HANDLE"

    return "LEGACY"


# ============================================================
# INSERT EVIDENCE
# ============================================================

def insert_evidence(
    cursor,
    row,
):
    evidence_id = int(
        row["evidence_id"]
    )

    actor_id = int(
        row["actor_id"]
    )

    description = (
        row["description"]
        or ""
    ).strip()

    evidence_type = (
        determine_evidence_type(
            description
        )
    )

    cursor.execute(
        """
        INSERT INTO evidence (
            evidence_id,
            actor_id,
            post_id,
            evidence_type,
            description,
            source,
            evidence_timestamp,
            confidence
        )
        VALUES (
            %s,
            %s,
            NULL,
            %s,
            %s,
            %s,
            NULL,
            NULL
        )
        ON CONFLICT (evidence_id)
        DO UPDATE SET
            actor_id = EXCLUDED.actor_id,
            evidence_type = EXCLUDED.evidence_type,
            description = EXCLUDED.description,
            source = EXCLUDED.source
        """,
        (
            evidence_id,
            actor_id,
            evidence_type,
            description,
            SOURCE_NAME,
        ),
    )


# ============================================================
# LOAD CSV
# ============================================================

def load_evidence():
    if not os.path.exists(EVIDENCE_FILE):
        raise FileNotFoundError(
            f"Evidence file not found:\n{EVIDENCE_FILE}"
        )

    connection = None
    cursor = None

    inserted = 0
    skipped = 0

    try:
        connection = get_connection()
        cursor = connection.cursor()

        print("=" * 60)
        print("DARKTRACE INTELLIGENCE")
        print("Evidence CSV Import")
        print("=" * 60)

        with open(
            EVIDENCE_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            required_columns = {
                "evidence_id",
                "actor_id",
                "description",
            }

            if not required_columns.issubset(
                set(reader.fieldnames or [])
            ):
                raise ValueError(
                    "evidence.csv must contain: "
                    "evidence_id, actor_id, description"
                )

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                try:
                    insert_evidence(
                        cursor,
                        row,
                    )

                    inserted += 1

                except Exception as error:
                    connection.rollback()

                    print(
                        f"Skipping row {row_number}: "
                        f"{error}"
                    )

                    skipped += 1

                    continue

        connection.commit()

        print("\nImport completed.")
        print(
            f"Rows processed : {inserted}"
        )
        print(
            f"Rows skipped   : {skipped}"
        )

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

        print(
            "PostgreSQL connection closed."
        )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    load_evidence()