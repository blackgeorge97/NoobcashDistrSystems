import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


from block import Block
from node import node
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
node = node(5)

#.......................................................................................



# get all transactions in the blockchain
@app.route('/transaction/create', methods=['POST'])
def create_transaction():
    data = request.get_json()
    id = data['receiver_id']
    amount = data['amount']
    for i in node.ring:
        if i['id'] == id:
            receiver_public_key = i['public_key']
            if node.create_transaction(wallet.public_key, receiver_public_key, amount):
                return 200
            else:
                return 300
    return 400

@app.route('/transaction/receive', methods=['POST'])
def receive_transaction():
    data = request.get_json()
    id = data['id']
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']
    input = data['inputs']
    output = data['outputs']
    signature = data['signature']
    if node.receive_transaction(id, sender, receiver, amount, input, output, signature):
        return 200
    return 400

@app.route('/transaction/get', methods=['GET'])
def get_transactions():
    response = {'balance': node.view_transactions()}
    return jsonify(response), 200

@app.route('/block/receive', methods=['POST'])
def receive_block():
    data = request.get_json()
    index = data['index']
    previous_hash = data['previous_hash']
    timestamp = data['timestamp']
    nonce = data['nonce']
    transactions = data['transactions']
    hash = data['hash']
    if not node.validate_block(index, previous_hash, timestamp, nonce, transactions, hash):
        node.resolve_conflicts()

@app.route('/blockchain/send', method=['GET'])
def return_blockchain():
    response = {'blockchain' : node.chain.to_dict()}
    return jsonify(response), 200


@app.route('/wallet/balance', methods=['GET'])
def return_balance():
    response = {'balance': node.wallet.balance()}
    return jsonify(response), 200


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)