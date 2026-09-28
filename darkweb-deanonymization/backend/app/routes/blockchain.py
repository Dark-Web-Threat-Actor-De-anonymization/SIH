from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.blockchain.evidence_service import (
    get_registered_evidence,
    register_database_evidence,
    register_evidence,
    verify_database_evidence,
    verify_evidence,
)


router = APIRouter(
    prefix="/blockchain",
    tags=["Blockchain Evidence"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class EvidenceRegistrationRequest(BaseModel):
    evidence_id: str = Field(..., min_length=1)
    evidence: dict[str, Any]


class EvidenceVerificationRequest(BaseModel):
    evidence: dict[str, Any]


# ============================================================
# BLOCKCHAIN STATUS
# ============================================================

@router.get("/status")
def blockchain_status():
    """
    Check whether the blockchain connection is available.
    """

    try:
        from app.blockchain.web3_client import (
            get_blockchain_status,
        )

        return get_blockchain_status()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# GENERIC / TEST REGISTRATION
# ============================================================

@router.post("/register")
def register_blockchain_evidence(
    request: EvidenceRegistrationRequest,
):
    """
    Hash supplied evidence and register the hash
    on the blockchain.

    This endpoint is retained for testing and
    generic evidence registration.
    """

    try:
        return register_evidence(
            request.evidence_id,
            request.evidence,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# REAL DATABASE EVIDENCE REGISTRATION
# ============================================================

@router.post("/register-from-db/{evidence_id}")
def register_evidence_from_database(
    evidence_id: int,
):
    """
    Fetch a real evidence record from PostgreSQL,
    hash it, register the hash on blockchain,
    and save the blockchain transaction metadata
    in PostgreSQL.
    """

    try:
        return register_database_evidence(
            evidence_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# RETRIEVE BLOCKCHAIN EVIDENCE
# ============================================================

@router.get("/evidence/{evidence_id}")
def get_blockchain_evidence(
    evidence_id: str,
):
    """
    Retrieve an evidence record stored on-chain.
    """

    try:
        return get_registered_evidence(
            evidence_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# ============================================================
# REAL DATABASE EVIDENCE VERIFICATION
# ============================================================

@router.get("/verify-from-db/{evidence_id}")
def verify_evidence_from_database(
    evidence_id: int,
):
    """
    Fetch the current PostgreSQL evidence,
    hash it again, and compare it with the
    blockchain-registered hash.
    """

    try:
        return verify_database_evidence(
            evidence_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# GENERIC / TEST VERIFICATION
# ============================================================

@router.post("/verify/{evidence_id}")
def verify_blockchain_evidence(
    evidence_id: str,
    request: EvidenceVerificationRequest,
):
    """
    Verify supplied evidence against its
    blockchain-registered hash.

    Retained for testing/generic usage.
    """

    try:
        return verify_evidence(
            evidence_id,
            request.evidence,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )