DARKTRACE INTELLIGENCE

Evidence-Driven Dark Web Threat Actor De-anonymization Platform

DarkTrace Intelligence is a cybersecurity investigation prototype for organizing authorized, synthetic, and privacy-safe threat intelligence and identifying analytical relationships between anonymous behavioral personas.

The platform combines:

Structured intelligence storage in PostgreSQL

DarkForums Safe Corpus ingestion

NLP-based linguistic and behavioral feature extraction

TF-IDF representation and KMeans behavioral clustering

Persona and relationship analysis

Explainable similarity/confidence signals

FastAPI REST APIs with Swagger/OpenAPI

Blockchain-backed evidence integrity using SHA-256, Solidity, Hardhat, and Web3.py

Safety / research note: The current prototype uses anonymized or synthetic data. Analytical personas and relationship scores are similarity signals, not proof of real-world identity or authorship. Any future external intelligence should be authorized, privacy-safe, and retain source provenance.

1. Problem Statement

SIH 2026 – Problem Statement 26151
Title: Dark Web Threat Actor De-anonymization
Theme: Blockchain & Cybersecurity
Category: Software

Dark web threat intelligence is often fragmented across posts, threads, handles, wallets, platforms, and evidence sources. Manually correlating these observations can make investigation slower and can make it difficult to distinguish strong evidence from weak similarity signals.

DarkTrace Intelligence provides a unified evidence-driven workflow:

Collect
   ↓
Normalize
   ↓
Store
   ↓
Extract Features
   ↓
Cluster Behavioral Patterns
   ↓
Compare Personas
   ↓
Calculate Confidence
   ↓
Preserve Evidence Integrity
   ↓
Expose REST APIs
   ↓
Visualize / Investigate

2. Current Implementation

Intelligence and AI/ML

The current prototype performs:

DarkForums Safe Corpus ingestion

PostgreSQL-backed post and thread storage

Linguistic feature extraction

Behavioral feature extraction

TF-IDF text representation

KMeans behavioral clustering

Analytical persona generation

Pairwise persona comparison

Linguistic similarity analysis

Behavioral similarity analysis

Topic similarity analysis

Temporal similarity analysis

Explainable relationship descriptions

The current local prototype data used during backend validation contains approximately:

Actors                  : 5
Posts                   : 154
Behavioral clusters     : 5
Post-cluster assignments: 152
Evidence records        : 3

The exact counts can change when the dataset is re-imported or regenerated.

3. Blockchain Evidence Integrity

Blockchain is used as an evidence-integrity and provenance layer, not as the primary data store.

What is stored where?

PostgreSQL
└── Raw / structured evidence records

SHA-256
└── Deterministic fingerprint of the evidence record

Blockchain / EvidenceRegistry
└── Evidence ID
└── Evidence hash
└── Registration timestamp
└── Submitting account

PostgreSQL / blockchain_evidence
└── Evidence ID
└── Evidence hash
└── Transaction hash
└── Block number
└── Registration time
└── Verification status

Raw evidence is not stored on-chain.

Verification workflow

Current PostgreSQL evidence
        ↓
Canonical JSON representation
        ↓
SHA-256 hash
        ↓
Compare with blockchain hash
        ↓
┌─────────────────────────────┐
│ Match    → VERIFIED         │
│ Mismatch → TAMPER_DETECTED  │
└─────────────────────────────┘

The blockchain workflow has been tested through FastAPI using:

Blockchain connectivity

Evidence registration

On-chain evidence retrieval

Generic evidence verification

Real PostgreSQL evidence registration

Real PostgreSQL evidence verification

Database tamper detection

The current development network is a local Hardhat network (chain_id 31337).

4. Technology Stack

Backend

Python

FastAPI

Uvicorn

PostgreSQL

psycopg2

Pydantic

python-dotenv

AI / Machine Learning

Pandas

NumPy

Scikit-learn

TF-IDF

KMeans

Blockchain

Solidity

Hardhat

Web3.py

SHA-256

Frontend / Integration

React / Node.js integration is handled separately by the frontend team.

Development Tools

Visual Studio Code

Git / GitHub

Postman / Swagger UI

pgAdmin

Neo4j, NetworkX, Sentence Transformers, advanced threat-technique mapping, and other planned analytical components are not treated as completed features in this README unless they are actually present and integrated in the repository.

5. Repository Structure

darkweb-deanonymization/
│
├── ai/
│   └── feature_extraction.py
│
├── backend/
│   ├── app/
│   │   ├── blockchain/
│   │   │   ├── __init__.py
│   │   │   ├── hasher.py
│   │   │   ├── web3_client.py
│   │   │   └── evidence_service.py
│   │   │
│   │   ├── routes/
│   │   │   ├── actors.py
│   │   │   ├── blockchain.py
│   │   │   ├── connections.py
│   │   │   ├── handles.py
│   │   │   ├── intelligence.py
│   │   │   ├── posts.py
│   │   │   ├── profile.py
│   │   │   └── search.py
│   │   │
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   └── requirements.txt
│
├── blockchain/
│   ├── contracts/
│   │   └── EvidenceRegistry.sol
│   ├── scripts/
│   │   ├── deploy.js
│   │   └── test-contract.js
│   ├── hardhat.config.ts
│   ├── package.json
│   └── .env
│
├── data/
│   ├── actors.csv
│   ├── evidence.csv
│   ├── handles.csv
│   ├── platforms.csv
│   ├── posts.csv
│   ├── wallets.csv
│   └── safe_corpus.jsonl
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── ingestion/
│   ├── darkforums_loader.py
│   ├── evidence_loader.py
│   └── legacy_csv_ingestion.py.py
│
├── scripts/
│   ├── init_db.sh
│   └── run_server.sh
│
├── .gitignore
└── README.md

Generated Hardhat directories such as artifacts/, cache/, and node_modules/ should remain ignored by Git.

6. Database Architecture

The PostgreSQL database stores structured investigation data and analytical results.

Core tables include:

actors
platforms
handles
threads
posts
evidence
persona_features
persona_relationships
behavioral_clusters
post_cluster_assignments
blockchain_evidence

Evidence tables

evidence stores the actual structured evidence record.

blockchain_evidence stores the blockchain registration and verification metadata associated with an evidence record.

This separation keeps sensitive/structured evidence off-chain while still providing a tamper-evident integrity reference.

7. Environment Configuration

PostgreSQL

Create a PostgreSQL database named:

darkweb

For the backend, use a local backend/.env containing both PostgreSQL and blockchain settings:

DB_HOST=localhost
DB_NAME=darkweb
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_PORT=5432

LOCAL_RPC_URL=http://127.0.0.1:8545
LOCAL_PRIVATE_KEY=YOUR_LOCAL_HARDHAT_ACCOUNT_PRIVATE_KEY
CONTRACT_ADDRESS=YOUR_DEPLOYED_EVIDENCE_REGISTRY_ADDRESS

The ingestion / ML scripts also require the PostgreSQL variables.

Never commit real passwords or private keys. Keep .env files local. The repository .gitignore excludes environment files.

8. Installation

Python dependencies

From the backend directory:

cd darkweb-deanonymization\backend
pip install -r requirements.txt

Blockchain dependencies

From the blockchain directory:

cd ..\blockchain
npm install

The blockchain project uses Hardhat with Solidity contracts.

9. Database Setup

Create the PostgreSQL database:

CREATE DATABASE darkweb;

Then execute the project schema:

database/schema.sql

Seed data can be loaded using:

database/seed.sql

For evidence records, the project includes a dedicated loader:

python ingestion/evidence_loader.py

10. Data Ingestion and ML Analysis

Import DarkForums data

Place the authorized / safe corpus at:

data/safe_corpus.jsonl

Run:

python ingestion/darkforums_loader.py

Run feature extraction and analysis

From the project root:

python ai/feature_extraction.py

The analysis pipeline follows:

PostgreSQL
    ↓
Load posts
    ↓
Feature extraction
    ↓
TF-IDF
    ↓
KMeans clustering
    ↓
Behavioral clusters
    ↓
Persona features
    ↓
Pairwise comparison
    ↓
Persona relationships

11. Blockchain Setup

Start the local Hardhat blockchain

Open a dedicated terminal:

cd darkweb-deanonymization\blockchain
npx hardhat node

Keep this terminal running.

Compile the contract

In another terminal:

cd darkweb-deanonymization\blockchain
npx hardhat compile

Deploy the contract

node scripts/deploy.js

Copy the printed contract address into:

backend/.env

as:

CONTRACT_ADDRESS=0x...

Restarting npx hardhat node creates a fresh local chain. Previously deployed contract addresses and local blockchain state will no longer be valid, so redeploy the contract and update CONTRACT_ADDRESS after a fresh Hardhat restart.

Optional contract test

node scripts/test-contract.js

The contract test demonstrates registration, retrieval, and hash verification including a modified-evidence case.

12. Run the FastAPI Backend

From:

 darkweb-deanonymization/backend

run:

uvicorn app.main:app --reload

The API runs at:

http://127.0.0.1:8000

Swagger/OpenAPI:

http://127.0.0.1:8000/docs

13. API Endpoints

Health

GET /
GET /health

Actors

GET /actors/
GET /actors/{actor_id}

Handles

GET /handles/
GET /handles/{handle_id}
GET /handles/actor/{actor_id}

Posts

GET /posts/
GET /posts/{post_id}

Profile

GET /actor/{actor_id}

Search

GET /search/?q=<query>

Intelligence

GET /intelligence/summary
GET /intelligence/personas
GET /intelligence/personas/{actor_id}
GET /intelligence/personas/{actor_id}/posts
GET /intelligence/relationships
GET /intelligence/relationships/{relationship_id}
GET /intelligence/clusters
GET /intelligence/clusters/{cluster_id}/posts

Blockchain evidence

GET  /blockchain/status
POST /blockchain/register
POST /blockchain/register-from-db/{evidence_id}
GET  /blockchain/evidence/{evidence_id}
POST /blockchain/verify/{evidence_id}
GET  /blockchain/verify-from-db/{evidence_id}

The generic /register and /verify/{evidence_id} endpoints are useful for integration testing.

The database-backed endpoints are the intended workflow for actual stored evidence:

POST /blockchain/register-from-db/{evidence_id}
GET  /blockchain/verify-from-db/{evidence_id}

14. Real Evidence → Blockchain Workflow

Registration

POST /blockchain/register-from-db/1
             ↓
Fetch evidence #1 from PostgreSQL
             ↓
Create deterministic SHA-256 hash
             ↓
EvidenceRegistry.registerEvidence()
             ↓
Blockchain transaction mined
             ↓
Store transaction hash + block number
in blockchain_evidence

Verification

GET /blockchain/verify-from-db/1
             ↓
Fetch current evidence #1
             ↓
Recalculate SHA-256
             ↓
Compare against on-chain hash
             ↓
VERIFIED
       or
TAMPER_DETECTED

15. Validation Completed

The backend integration has been tested locally for:

✅ FastAPI startup
✅ Swagger/OpenAPI documentation
✅ PostgreSQL connectivity
✅ Blockchain connectivity
✅ Contract deployment
✅ Contract registration
✅ Contract retrieval
✅ Generic hash verification
✅ Real PostgreSQL evidence registration
✅ Real PostgreSQL evidence verification
✅ PostgreSQL blockchain audit record
✅ Database tamper detection

A tamper test changed an existing evidence description in PostgreSQL and the verification endpoint returned:

verified: false
verification_status: TAMPER_DETECTED

After restoring the original evidence, verification returned:

verified: true
verification_status: VERIFIED

16. Explainability and Safety

DarkTrace Intelligence distinguishes between:

Observed evidence
       ↓
Analytical similarity
       ↓
Confidence signal
       ↓
Verified identity

These are not interchangeable.

The current Safe Corpus anonymizes / redacts author identity information. The prototype therefore treats generated clusters as analytical behavioral personas, not confirmed real-world individuals.

The system is intended for authorized, privacy-safe cybersecurity research and investigation workflows. It should not be used to expose, identify, or target private individuals without appropriate authorization and legal basis.

17. Frontend Integration

The frontend team can use the FastAPI Swagger specification at:

http://127.0.0.1:8000/docs

The frontend can consume the intelligence and blockchain APIs directly.

For the evidence-integrity UI, a typical workflow is:

Select Evidence
      ↓
Register Evidence
      ↓
Show transaction / block reference
      ↓
Verify Evidence
      ↓
Display VERIFIED / TAMPER_DETECTED

The frontend is developed separately from the backend service.

18. Development Status

PostgreSQL database              ✅
Safe Corpus ingestion            ✅
Feature extraction               ✅
TF-IDF analysis                  ✅
KMeans clustering                ✅
Behavioral personas              ✅
Relationship analysis            ✅
FastAPI backend                  ✅
Swagger/OpenAPI                  ✅
Blockchain contract              ✅
Hardhat local network            ✅
Web3.py integration              ✅
Evidence hashing                 ✅
Database-backed registration     ✅
Database-backed verification     ✅
Tamper detection                 ✅
Frontend integration             🔄
Advanced graph / NLP extensions  🔄

19. Project References

The project presentation references:

MITRE ATT&CK

Tor Project documentation

Neo4j documentation

Scikit-learn documentation

These references support the cybersecurity, dark-web, graph-analysis, and machine-learning concepts described by the project.

20. Repository

GitHub:

https://github.com/Dark-Web-Threat-Actor-De-anonymization/SIH

License / Usage

This repository is a Smart India Hackathon prototype. Use only authorized, synthetic, anonymized, or otherwise legally permitted data for testing and demonstrations.