from typing import Any, Mapping

from app.crud import (
    execute_query,
    fetch_one,
)

from .hasher import hash_evidence
from .web3_client import (
    account,
    get_contract,
    w3,
)


# ============================================================
# GENERIC / TEST FUNCTIONS
# ============================================================

def register_evidence(
    evidence_id: str,
    evidence: Mapping[str, Any],
) -> dict:
    """
    Hash supplied evidence and register its hash
    on the blockchain.
    """

    if not evidence_id:
        raise ValueError("evidence_id is required")

    evidence_hash = hash_evidence(evidence)

    contract = get_contract()

    nonce = w3.eth.get_transaction_count(
        account.address,
        "pending",
    )

    transaction = (
        contract
        .functions
        .registerEvidence(
            evidence_id,
            evidence_hash,
        )
        .build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "chainId": w3.eth.chain_id,
            }
        )
    )

    signed_transaction = account.sign_transaction(
        transaction
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    return {
        "evidence_id": evidence_id,
        "evidence_hash": evidence_hash,
        "transaction_hash": tx_hash.hex(),
        "block_number": receipt["blockNumber"],
        "status": receipt["status"],
        "registered": receipt["status"] == 1,
    }


def get_registered_evidence(
    evidence_id: str,
) -> dict:
    """
    Retrieve evidence information stored on-chain.
    """

    if not evidence_id:
        raise ValueError("evidence_id is required")

    contract = get_contract()

    record = (
        contract
        .functions
        .getEvidence(evidence_id)
        .call()
    )

    return {
        "evidence_id": record[0],
        "evidence_hash": record[1],
        "timestamp": record[2],
        "submitted_by": record[3],
    }


def verify_evidence(
    evidence_id: str,
    evidence: Mapping[str, Any],
) -> dict:
    """
    Hash supplied evidence and compare it with
    the blockchain-registered hash.
    """

    if not evidence_id:
        raise ValueError("evidence_id is required")

    current_hash = hash_evidence(evidence)

    contract = get_contract()

    verified = (
        contract
        .functions
        .verifyEvidence(
            evidence_id,
            current_hash,
        )
        .call()
    )

    return {
        "evidence_id": evidence_id,
        "current_hash": current_hash,
        "verified": verified,
    }


# ============================================================
# DATABASE-BACKED FUNCTIONS
# ============================================================

def get_database_evidence(
    evidence_id: int,
) -> dict:
    """
    Fetch an evidence record from PostgreSQL.
    """

    if evidence_id is None:
        raise ValueError(
            "evidence_id is required"
        )

    evidence = fetch_one(
        """
        SELECT
            evidence_id,
            actor_id,
            post_id,
            evidence_type,
            description,
            source,
            evidence_timestamp,
            confidence,
            created_at
        FROM evidence
        WHERE evidence_id = %s
        """,
        (evidence_id,),
    )

    if not evidence:
        raise ValueError(
            f"Evidence {evidence_id} not found in PostgreSQL"
        )

    return evidence


def get_blockchain_audit_record(
    evidence_id: int,
) -> dict | None:
    """
    Fetch blockchain audit information from PostgreSQL.
    """

    return fetch_one(
        """
        SELECT
            blockchain_evidence_id,
            evidence_id,
            evidence_hash,
            blockchain_network,
            transaction_hash,
            block_number,
            registered_at,
            verification_status
        FROM blockchain_evidence
        WHERE evidence_id = %s
        """,
        (evidence_id,),
    )


def register_database_evidence(
    evidence_id: int,
) -> dict:
    """
    Fetch a real evidence record from PostgreSQL,
    hash it, register the hash on blockchain,
    and store the blockchain transaction metadata
    in PostgreSQL.
    """

    if evidence_id is None:
        raise ValueError(
            "evidence_id is required"
        )

    # --------------------------------------------------------
    # 1. Fetch real evidence from PostgreSQL
    # --------------------------------------------------------

    evidence = get_database_evidence(
        evidence_id
    )

    evidence_payload = dict(evidence)

    # --------------------------------------------------------
    # 2. Generate SHA-256 hash
    # --------------------------------------------------------

    evidence_hash = hash_evidence(
        evidence_payload
    )

    # --------------------------------------------------------
    # 3. Check PostgreSQL audit table first
    # --------------------------------------------------------

    existing_audit = (
        get_blockchain_audit_record(
            evidence_id
        )
    )

    if existing_audit:
        return {
            "evidence_id": evidence_id,
            "evidence_hash": existing_audit[
                "evidence_hash"
            ],
            "transaction_hash": existing_audit[
                "transaction_hash"
            ],
            "block_number": existing_audit[
                "block_number"
            ],
            "blockchain_network": existing_audit[
                "blockchain_network"
            ],
            "verification_status": existing_audit[
                "verification_status"
            ],
            "registered": True,
            "message": (
                "Evidence is already registered."
            ),
        }

    # --------------------------------------------------------
    # 4. Check whether already registered on blockchain
    # --------------------------------------------------------

    contract = get_contract()

    blockchain_evidence_id = str(
        evidence_id
    )

    try:
        existing_record = (
            contract
            .functions
            .getEvidence(
                blockchain_evidence_id
            )
            .call()
        )

        if existing_record[2] != 0:
            raise ValueError(
                f"Evidence {evidence_id} is already "
                "registered on the blockchain."
            )

    except ValueError:
        raise

    except Exception:
        # Evidence not found on-chain.
        # This is expected for a new record.
        pass

    # --------------------------------------------------------
    # 5. Create transaction
    # --------------------------------------------------------

    nonce = w3.eth.get_transaction_count(
        account.address,
        "pending",
    )

    transaction = (
        contract
        .functions
        .registerEvidence(
            blockchain_evidence_id,
            evidence_hash,
        )
        .build_transaction(
            {
                "from": account.address,
                "nonce": nonce,
                "chainId": w3.eth.chain_id,
            }
        )
    )

    # --------------------------------------------------------
    # 6. Sign transaction
    # --------------------------------------------------------

    signed_transaction = account.sign_transaction(
        transaction
    )

    # --------------------------------------------------------
    # 7. Send transaction
    # --------------------------------------------------------

    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    # --------------------------------------------------------
    # 8. Wait for confirmation
    # --------------------------------------------------------

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    if receipt["status"] != 1:
        raise RuntimeError(
            "Blockchain transaction failed."
        )

    transaction_hash = tx_hash.hex()
    block_number = receipt["blockNumber"]

    # --------------------------------------------------------
    # 9. Save blockchain metadata in PostgreSQL
    # --------------------------------------------------------

    execute_query(
        """
        INSERT INTO blockchain_evidence (
            evidence_id,
            evidence_hash,
            blockchain_network,
            transaction_hash,
            block_number,
            verification_status
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            evidence_id,
            evidence_hash,
            "hardhat-local",
            transaction_hash,
            block_number,
            "REGISTERED",
        ),
    )

    return {
        "evidence_id": evidence_id,
        "evidence_hash": evidence_hash,
        "transaction_hash": transaction_hash,
        "block_number": block_number,
        "blockchain_network": "hardhat-local",
        "verification_status": "REGISTERED",
        "registered": True,
    }


def verify_database_evidence(
    evidence_id: int,
) -> dict:
    """
    Fetch current PostgreSQL evidence, hash it again,
    and compare the hash against blockchain.
    """

    if evidence_id is None:
        raise ValueError(
            "evidence_id is required"
        )

    # --------------------------------------------------------
    # 1. Fetch current database evidence
    # --------------------------------------------------------

    evidence = get_database_evidence(
        evidence_id
    )

    evidence_payload = dict(evidence)

    # --------------------------------------------------------
    # 2. Generate current hash
    # --------------------------------------------------------

    current_hash = hash_evidence(
        evidence_payload
    )

    # --------------------------------------------------------
    # 3. Get blockchain record
    # --------------------------------------------------------

    contract = get_contract()

    blockchain_evidence_id = str(
        evidence_id
    )

    record = (
        contract
        .functions
        .getEvidence(
            blockchain_evidence_id
        )
        .call()
    )

    registered_hash = record[1]
    blockchain_timestamp = record[2]
    submitted_by = record[3]

    # --------------------------------------------------------
    # 4. Compare hashes
    # --------------------------------------------------------

    verified = (
        current_hash
        == registered_hash
    )

    # --------------------------------------------------------
    # 5. Update audit status
    # --------------------------------------------------------

    verification_status = (
        "VERIFIED"
        if verified
        else "TAMPER_DETECTED"
    )

    execute_query(
        """
        UPDATE blockchain_evidence
        SET verification_status = %s
        WHERE evidence_id = %s
        """,
        (
            verification_status,
            evidence_id,
        ),
    )

    # --------------------------------------------------------
    # 6. Get audit record
    # --------------------------------------------------------

    audit_record = (
        get_blockchain_audit_record(
            evidence_id
        )
    )

    return {
        "evidence_id": evidence_id,
        "current_hash": current_hash,
        "blockchain_hash": registered_hash,
        "verified": verified,
        "verification_status": verification_status,
        "blockchain_timestamp": blockchain_timestamp,
        "submitted_by": submitted_by,
        "transaction_hash": (
            audit_record["transaction_hash"]
            if audit_record
            else None
        ),
        "block_number": (
            audit_record["block_number"]
            if audit_record
            else None
        ),
    }