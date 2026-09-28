import json
import os
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


RPC_URL = os.getenv("LOCAL_RPC_URL")
PRIVATE_KEY = os.getenv("LOCAL_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")


if not RPC_URL:
    raise RuntimeError("Missing LOCAL_RPC_URL in .env")

if not PRIVATE_KEY:
    raise RuntimeError("Missing LOCAL_PRIVATE_KEY in .env")

if not CONTRACT_ADDRESS:
    raise RuntimeError("Missing CONTRACT_ADDRESS in .env")


# --------------------------------------------------
# Connect to blockchain
# --------------------------------------------------

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise RuntimeError(
        f"Could not connect to blockchain at {RPC_URL}"
    )


# --------------------------------------------------
# Load contract ABI
# --------------------------------------------------

# backend/app/blockchain/web3_client.py
#                       ↑
# project root is three levels above this file
PROJECT_ROOT = Path(__file__).resolve().parents[3]

ABI_PATH = (
    PROJECT_ROOT
    / "blockchain"
    / "artifacts"
    / "contracts"
    / "EvidenceRegistry.sol"
    / "EvidenceRegistry.json"
)


if not ABI_PATH.exists():
    raise FileNotFoundError(
        f"Contract ABI not found at: {ABI_PATH}\n"
        "Run `npx hardhat compile` first."
    )


with open(ABI_PATH, "r", encoding="utf-8") as file:
    contract_artifact = json.load(file)


CONTRACT_ABI = contract_artifact["abi"]


# --------------------------------------------------
# Contract instance
# --------------------------------------------------

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=CONTRACT_ABI,
)


# --------------------------------------------------
# Blockchain account
# --------------------------------------------------

account = w3.eth.account.from_key(PRIVATE_KEY)
ACCOUNT_ADDRESS = account.address


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def get_blockchain_status() -> dict:
    """
    Return basic blockchain connection information.
    """

    return {
        "connected": w3.is_connected(),
        "rpc_url": RPC_URL,
        "chain_id": w3.eth.chain_id,
        "account": ACCOUNT_ADDRESS,
        "contract_address": CONTRACT_ADDRESS,
    }


def get_contract():
    """
    Return the EvidenceRegistry contract instance.
    """

    return contract