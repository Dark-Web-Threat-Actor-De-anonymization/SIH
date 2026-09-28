import "dotenv/config";
import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// --------------------------------------------------
// Resolve the current script directory
// --------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --------------------------------------------------
// Load configuration from .env
// --------------------------------------------------

const RPC_URL = process.env.LOCAL_RPC_URL;
const PRIVATE_KEY = process.env.LOCAL_PRIVATE_KEY;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;

if (!RPC_URL) {
    throw new Error("Missing LOCAL_RPC_URL in blockchain/.env");
}

if (!PRIVATE_KEY) {
    throw new Error("Missing LOCAL_PRIVATE_KEY in blockchain/.env");
}

if (!CONTRACT_ADDRESS) {
    throw new Error("Missing CONTRACT_ADDRESS in blockchain/.env");
}

// --------------------------------------------------
// Load compiled contract artifact
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
        "Run `npx hardhat compile` first."
    );
}

const artifact = JSON.parse(
    fs.readFileSync(artifactPath, "utf8")
);

// --------------------------------------------------
// Connect to local Hardhat blockchain
// --------------------------------------------------

const provider = new ethers.JsonRpcProvider(RPC_URL);

const wallet = new ethers.Wallet(
    PRIVATE_KEY,
    provider
);

console.log("Connected account:", wallet.address);
console.log("Contract address:", CONTRACT_ADDRESS);

// --------------------------------------------------
// Create contract instance
// --------------------------------------------------

const contract = new ethers.Contract(
    CONTRACT_ADDRESS,
    artifact.abi,
    wallet
);

// --------------------------------------------------
// Test evidence
// --------------------------------------------------

const evidenceId = "EVIDENCE-TEST-002";

// 64-character SHA-256-style test hash
const evidenceHash =
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

console.log("\n----------------------------------------");
console.log("1. Registering test evidence");
console.log("----------------------------------------");

try {
    const tx = await contract.registerEvidence(
        evidenceId,
        evidenceHash
    );

    console.log("Transaction submitted:", tx.hash);

    await tx.wait();

    console.log("Evidence registered successfully.");
} catch (error) {
    console.error("Registration failed.");

    if (error.reason) {
        console.error("Reason:", error.reason);
    } else {
        console.error(error.message);
    }

    process.exit(1);
}

// --------------------------------------------------
// Retrieve evidence
// --------------------------------------------------

console.log("\n----------------------------------------");
console.log("2. Reading stored evidence");
console.log("----------------------------------------");

try {
    const record = await contract.getEvidence(
        evidenceId
    );

    console.log("Evidence ID:", record[0]);
    console.log("Stored hash:", record[1]);
    console.log("Timestamp:", record[2].toString());
    console.log("Submitted by:", record[3]);
} catch (error) {
    console.error("Could not retrieve evidence.");
    console.error(error.message);
    process.exit(1);
}

// --------------------------------------------------
// Verify original hash
// --------------------------------------------------

console.log("\n----------------------------------------");
console.log("3. Verify original evidence");
console.log("----------------------------------------");

try {
    const verified = await contract.verifyEvidence(
        evidenceId,
        evidenceHash
    );

    console.log(
        "Verification with original hash:",
        verified
    );
} catch (error) {
    console.error("Verification failed.");
    console.error(error.message);
    process.exit(1);
}

// --------------------------------------------------
// Verify modified/tampered hash
// --------------------------------------------------

console.log("\n----------------------------------------");
console.log("4. Verify modified evidence");
console.log("----------------------------------------");

const tamperedHash =
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

try {
    const tamperedVerification =
        await contract.verifyEvidence(
            evidenceId,
            tamperedHash
        );

    console.log(
        "Verification with modified hash:",
        tamperedVerification
    );
} catch (error) {
    console.error("Tampered verification failed.");
    console.error(error.message);
    process.exit(1);
}

// --------------------------------------------------
// Test complete
// --------------------------------------------------

console.log("\n========================================");
console.log("Blockchain evidence test completed.");
console.log("========================================");