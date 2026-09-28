import "dotenv/config";
import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// --------------------------------------------------
// Resolve this script's directory
// --------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --------------------------------------------------
// Environment configuration
// --------------------------------------------------

const RPC_URL = process.env.LOCAL_RPC_URL;
const PRIVATE_KEY = process.env.LOCAL_PRIVATE_KEY;

if (!RPC_URL) {
    throw new Error("Missing LOCAL_RPC_URL in blockchain/.env");
}

if (!PRIVATE_KEY) {
    throw new Error("Missing LOCAL_PRIVATE_KEY in blockchain/.env");
}

// --------------------------------------------------
// Contract artifact
// --------------------------------------------------

const artifactPath = path.join(
    __dirname,
    "..",
    "artifacts",
    "contracts",
    "EvidenceRegistry.sol",
    "EvidenceRegistry.json"
);

if (!fs.existsSync(artifactPath)) {
    throw new Error(
        `Contract artifact not found at:\n${artifactPath}\n\n` +
        "Run: npx hardhat compile"
    );
}

const artifact = JSON.parse(
    fs.readFileSync(artifactPath, "utf8")
);

// --------------------------------------------------
// Connect to local Hardhat blockchain
// --------------------------------------------------

const provider = new ethers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log("Deploying with account:", wallet.address);

// --------------------------------------------------
// Check account balance
// --------------------------------------------------

const balance = await provider.getBalance(wallet.address);

console.log(
    "Account balance:",
    ethers.formatEther(balance),
    "ETH"
);

// --------------------------------------------------
// Deploy contract
// --------------------------------------------------

const factory = new ethers.ContractFactory(
    artifact.abi,
    artifact.bytecode,
    wallet
);

console.log("Deploying EvidenceRegistry...");

const contract = await factory.deploy();

console.log(
    "Deployment transaction:",
    contract.deploymentTransaction().hash
);

await contract.waitForDeployment();

// --------------------------------------------------
// Deployment details
// --------------------------------------------------

const contractAddress = await contract.getAddress();

console.log("");
console.log("========================================");
console.log("EvidenceRegistry deployed successfully!");
console.log("========================================");
console.log("Contract address:", contractAddress);
console.log("Owner:", await contract.owner());
console.log("========================================");