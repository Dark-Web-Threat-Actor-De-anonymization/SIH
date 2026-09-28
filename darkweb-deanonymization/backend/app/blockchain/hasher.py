import hashlib
import json
from typing import Any, Mapping


def canonicalize_evidence(evidence: Mapping[str, Any]) -> str:
    """
    Convert an evidence record into a deterministic JSON string.

    Sorting keys and using fixed separators ensures that the same
    logical evidence produces the same SHA-256 hash.
    """
    return json.dumps(
        evidence,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def hash_evidence(evidence: Mapping[str, Any]) -> str:
    """
    Generate a SHA-256 hash for an evidence record.

    Returns:
        64-character hexadecimal SHA-256 hash.
    """
    canonical_data = canonicalize_evidence(evidence)

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()


def hash_text(text: str) -> str:
    """
    Generate a SHA-256 hash for plain text.
    """
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()