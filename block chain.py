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
            nonce=self.proof_of_work(0, genesis_hash, []),
            election_data={'data': 'Initial Election Data'}  # Data pemilu awal
        )

    def proof_of_work(self, index, hash_of_previous_block, transactions, nonce=0):
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        return nonce
    
    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        content = f'{index}{hash_of_previous_block}{json.dumps(transactions)}{nonce}'.encode()
        content_hash = hashlib.sha256(content).hexdigest()
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target

    def append_block(self, hash_of_previous_block, nonce, election_data):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'election_data': election_data,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, voter_id, candidate):
        transaction = {'voter_id': voter_id, 'candidate': candidate}
        self.current_transactions.append(transaction)
        return len(self.chain) + 1  # Index of the block that will hold this transaction

    @property
    def last_block(self):
        return self.chain[-1]

# Inisialisasi Flask
app = Flask(__name__)

# Instance dari Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_nonce = last_block['nonce']
    last_hash = blockchain.hash_block(last_block)
    nonce = blockchain.proof_of_work(last_block['index'], last_hash, blockchain.current_transactions)

    # Menambahkan blok baru ke rantai
    election_data = {'data': 'Contoh data pemilu'}
    block = blockchain.append_block(last_hash, nonce, election_data)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'election_data': block['election_data'],
        'nonce': block['nonce'],
        'previous_hash': block['hash_of_previous_block'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['voter_id', 'candidate']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['voter_id'], values['candidate'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)