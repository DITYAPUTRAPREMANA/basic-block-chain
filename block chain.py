import sys
import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask
from flask import request
from flask import jsonify

import requests
from urllib.parse import urlparse

class Blockchain(object):
    difficulty_target = "0000"

    def hash_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()
    
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        genesis_hash = self.hash_block("genesis_block")

        # Menambahkan blok genesis
        self.append_block(
            hash_of_previous_block=genesis_hash,
            nonce=self.proof_of_work(0, genesis_hash, [])
        )

    def proof_of_work(self, index, hash_of_previous_block, transactions, nonce=0):
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{json.dumps(transactions)}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target

    def append_block(self, hash_of_previous_block, nonce):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block,
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

# Inisialisasi Flask
app = Flask(__name__)

# Instance dari Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Implementasi fungsi mining
    return "We'll add mining functionality here"

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # Implementasi fungsi untuk menambahkan transaksi baru
    return "We'll add new transaction functionality here"

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


