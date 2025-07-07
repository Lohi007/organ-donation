import hashlib
import csv
import os
import json
import time


# Block Class
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


# Blockchain Class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block in the blockchain (genesis block)
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def add_block(self, data):
        # Get the previous block's hash
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), time.time(), data, previous_block.hash)
        self.chain.append(new_block)

    def get_latest_block(self):
        return self.chain[-1]

    def display_blockchain(self):
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}\n")

    def export_to_json(self, file_name):
        # Convert the blockchain to a list of dictionaries and save it to a JSON file
        blockchain_data = [block.to_dict() for block in self.chain]
        with open(file_name, 'w') as json_file:
            json.dump(blockchain_data, json_file, indent=4)


# Function to process CSV and update blockchain once
def process_csv_and_update_blockchain(file_path, blockchain):
    # Read the CSV file and append data to the blockchain
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            # Creating a simple string of row data to store in the blockchain
            row_data = f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Blood Type: {row[3]}, Organs: {row[4]}, Contact Info: {row[5]}"
            blockchain.add_block(row_data)

    # Export the updated blockchain to a JSON file
    blockchain.export_to_json("blockchain_data.json")

    # Display the updated blockchain
    blockchain.display_blockchain()


# Main Code
def main():
    blockchain = Blockchain()


    # Path to the CSV file you uploaded
    file_path = "organ_donation.csv"

    # Process the CSV file and update the blockchain once
    process_csv_and_update_blockchain(file_path, blockchain)


# if __name__ == "__main__":
#     main()
