// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title EvidenceRegistry
 * @notice Registers cryptographic hashes of investigation evidence
 *         for tamper-evident verification.
 *
 * Raw evidence is NOT stored on-chain.
 * Only its identifier, hash, registration timestamp,
 * and submitting address are stored.
 */
contract EvidenceRegistry {

    struct Evidence {
        string evidenceId;
        string evidenceHash;
        uint256 timestamp;
        address submittedBy;
    }

    address public owner;

    mapping(string => Evidence) private evidenceRecords;

    event EvidenceRegistered(
        string indexed evidenceId,
        string evidenceHash,
        uint256 timestamp,
        address indexed submittedBy
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Register an evidence hash.
     *         An evidence ID can only be registered once.
     */
    function registerEvidence(
        string calldata evidenceId,
        string calldata evidenceHash
    ) external onlyOwner {

        require(
            bytes(evidenceId).length > 0,
            "Evidence ID required"
        );

        require(
            bytes(evidenceHash).length > 0,
            "Evidence hash required"
        );

        require(
            evidenceRecords[evidenceId].timestamp == 0,
            "Evidence already registered"
        );

        evidenceRecords[evidenceId] = Evidence({
            evidenceId: evidenceId,
            evidenceHash: evidenceHash,
            timestamp: block.timestamp,
            submittedBy: msg.sender
        });

        emit EvidenceRegistered(
            evidenceId,
            evidenceHash,
            block.timestamp,
            msg.sender
        );
    }

    /**
     * @notice Retrieve registered evidence.
     */
    function getEvidence(
        string calldata evidenceId
    )
        external
        view
        returns (
            string memory,
            string memory,
            uint256,
            address
        )
    {
        require(
            evidenceRecords[evidenceId].timestamp != 0,
            "Evidence not found"
        );

        Evidence memory record = evidenceRecords[evidenceId];

        return (
            record.evidenceId,
            record.evidenceHash,
            record.timestamp,
            record.submittedBy
        );
    }

    /**
     * @notice Verify that a current hash matches
     *         the hash registered on-chain.
     */
    function verifyEvidence(
        string calldata evidenceId,
        string calldata currentHash
    )
        external
        view
        returns (bool)
    {
        Evidence memory record = evidenceRecords[evidenceId];

        require(
            record.timestamp != 0,
            "Evidence not found"
        );

        return keccak256(
            bytes(record.evidenceHash)
        ) == keccak256(
            bytes(currentHash)
        );
    }
}