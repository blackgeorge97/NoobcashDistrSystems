#from crypt import methods
from tkinter.font import BOLD
from urllib import response
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from block import Block
from node import node
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction
from argparse import ArgumentParser
import time
import threading


bootstrap_ip = '127.0.0.1'
bootstrap_port = '5000'

parser = ArgumentParser()
parser.add_argument('-ip', '--ip', default='127.0.0.1', type=str, help='Hosting ip')
parser.add_argument('-p', '--port', default='5000', type=str, help='port to listen on')
parser.add_argument('-b', '--bootstrap', default=False, type=bool, help='Bootstrap node or not')
parser.add_argument('-n', '--nodes', default=0, type=int, help='Total number of nodes')
parser
args = parser.parse_args()
ip = args.ip
port = args.port
bootstrap = args.bootstrap
nodes = args.nodes

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

node = node(bootstrap, ip, port, nodes, bootstrap_ip, bootstrap_port)

#CORS(app)

#.......................................................................................


@app.route('/network/register', methods=['POST'])
def register_node():
    data = request.get_json()
    address = data['address']
    public_key = data['public_key']
    node.register_node_to_ring(address, public_key)
    response = {'Status' : 'Success'}
    return jsonify(response), 200


@app.route('/network/receive', methods=['POST'])
def receive_reg_data():
    data = request.get_json()
    ring = data['ring']
    block = data['genesis_block']
    index = block['index']
    previous_hash = block['previous_hash']
    timestamp = block['timestamp']
    nonce = block['nonce']
    transactions = block['transactions']
    hash = block['hash']
    node.receive_reg_info(ring, index, timestamp, previous_hash, nonce, transactions, hash)
    response = {'Status' : 'Success'}
    return jsonify(response), 200


@app.route('/transaction/create', methods=['POST'])
def create_transaction():
    data = request.get_json()
    id = data['receiver_id']
    amount = data['amount']
    for i in node.ring:
        if i['id'] == id:
            receiver_public_key = i['public_key']
            if node.create_transaction(node.wallet.public_key, receiver_public_key, amount):
                response = {'Status' : 'success'}
                return jsonify(response), 200
            else:
                response = {'Status' : 'Failure: Not enough nbcs'}
                return jsonify(response), 201
    
    response = {'Status' : 'Node does not exist'}
    return jsonify(response), 202

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
        response = {'Status' : 'success'}
        return jsonify(response), 200
    response = {'Status' : 'Failure: Could not validate transaction'}
    return jsonify(response), 201

@app.route('/transaction/get', methods=['GET'])
def get_transactions():
    response = {'transactions': node.view_transactions()}
    return jsonify(response), 200

@app.route('/block/receive', methods=['POST'])
def receive_block():
    data = request.get_json()
    block = data['block']
    index = block['index']
    previous_hash = block['previous_hash']
    timestamp = block['timestamp']
    nonce = block['nonce']
    transactions = block['transactions']
    hash = block['hash']
    queue = data['tran_queue']
    if not node.validate_block(index, previous_hash, timestamp, nonce, transactions, hash, queue):
        response = {'Status': 'Concencus'}
        return jsonify(response), 201
    response = {'Status': 'Success'}
    return jsonify(response), 200

@app.route('/blockchain/send', methods=['GET'])
def return_blockchain():
    response = {'blockchain' : node.chain.to_dict(), 'tran_queue' : node.tran_queue}
    return jsonify(response), 200


@app.route('/wallet/balance', methods=['GET'])
def return_balance():
    response = {'balance': node.wallet.balance()}
    return jsonify(response), 200

@app.route('/ring', methods=['GET'])
def return_ring():
    response = {'ring' : node.ring}
    return jsonify(response), 200




# run it once fore every node

if __name__ == '__main__':
    app.run(host=ip, port=port)