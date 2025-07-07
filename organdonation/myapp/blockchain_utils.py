import json
import time
import hashlib
import os

# Constants for file paths
BLOCKCHAIN_FILE = os.path.join(os.path.dirname(__file__), "blockchain_data.json")

def create_block(index, previous_hash, donor_info):
    """Generate a block with proper donor information in JSON format."""
    timestamp = time.time()
    data = json.dumps(donor_info)  # Ensure data is serialized to JSON string
    block_string = f"{index}{timestamp}{data}{previous_hash}"
    block_hash = hashlib.sha256(block_string.encode()).hexdigest()

    return {
        'index': index,
        'timestamp': timestamp,
        'data': data,  # Store data as JSON string
        'previous_hash': previous_hash,
        'hash': block_hash
    }

def load_blockchain():
    """Load blockchain data from the JSON file."""
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, 'r') as f:
            return json.load(f)
    return []

def save_blockchain(blockchain):
    """Save blockchain to a JSON file."""
    with open(BLOCKCHAIN_FILE, 'w') as f:
        json.dump(blockchain, f, indent=4)
