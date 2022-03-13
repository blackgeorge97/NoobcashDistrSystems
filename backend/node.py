from ensurepip import bootstrap
from block import Block
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction
import json
import requests
from random import randint

MINING_DIFFICULTY = 4
CAPACITY = 1
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class node:
	def __init__(self, bootstrap, ip, port, n):
		##set
		self.chain = Blockchain()
		self.current_id_count = 0
		self.wallet = wallet()
		self.utxos_per_node = {}
		self.mining = False
		self.cur_block
		self.id = -1
		temp_addr = ip + ':' + port
		self.ring = []  #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
		if (bootstrap):
			self.id = 0
			temp_node = {'id' : 0, 'address' : temp_addr, 'public_key' : self.wallet.public_key}
			self.ring.append(temp_node)
			self.utxos_per_node[self.wallet.public_key] = []
		else:
			return
	 		
	
	def register_node_to_ring(self):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		
		return


	def create_transaction(self, sender, receiver, amount):
		#remember to broadcast it
		total_sum = 0
		used_tran = []
		for utxo in self.utxos_per_nodes[sender]:
			total_sum += utxo['amount']
			used_tran.append(utxo)
			if(total_sum >= amount):
				break
		if (total_sum < amount):
			print("not enough nbc")
			return False
		for used in used_tran:
			self.utxos_per_nodes[sender].remove(used)
			self.wallet.utxos.remove(used)
		self.ring[sender]['balance'] -= (total_sum - amount)
		self.ring[receiver]['balance'] += amount
		new_tran = Transaction(sender, receiver, amount, used_tran)
		outputs = []
		out1 = {
			'id' : new_tran.transaction_id,
			'receiver' : new_tran.receiver_address,
			'amount' : new_tran.amount
		}
		outputs.append(out1)
		self.utxos_per_nodes[receiver].append(out1)
		if (total_sum > amount):
			out2 = {
				'id' : new_tran.transaction_id,
				'receiver' : new_tran.sender_address,
				'amount' : total_sum - new_tran.amount
			}
			outputs.append(out2)
			self.utxos_per_nodes[sender].append(out2)
			self.wallet.utxos.append(out2)
		new_tran.transaction_outputs = outputs
		new_tran.Signature = new_tran.sign_transaction(self.wallet.private_key)
		self.broadcast_transaction(new_tran)
		self.add_transaction_to_block(new_tran)
		return True
        

	def broadcast_transaction(self, tran):
		message = tran.to_dict_signed()
		message_json = json.dumps(message)
		for node in self.ring:
			if node['id'] == self.id:
				continue
			requests.post(node['address'] + "/transaction/receive", data = message_json, headers = headers)


	def validate_transaction(self, transaction, signature, public_key):
		#use of signature and NBCs balance
		for input in transaction.input:
			if input not in self.utxos_per_node[transaction.sender]:
				return False
		if transaction.verify_signature(public_key, signature):
			return True
		return False
 
	def receive_transaction(self, id, sender, receiver, amount, input, output, signature):
		new_tran = Transaction(sender, receiver, amount, input)
		new_tran.id = id 
		new_tran.transaction_outputs = output
		if not self.validate_transaction(new_tran, signature, sender):
			return False
		new_tran.Signature = signature
		for i in input:
			self.utxos_per_node[sender].remove(i)
		for i in output:
			self.utxos_per_node[i[receiver]].append(i)
			if (i[receiver] == self.wallet.public_key):
				self.wallet.utxos.append(i)
		self.add_transaction_to_block(new_tran)
		return True
	
	def view_transactions(self):
		return self.chain.cur_block().listOfTransactions

	def add_transaction_to_block(self, tran):
		#if enough transactions  mine
		block = self.cur_block
		block.add_transaction(tran)
		if (len(block.listOfTransactions) == CAPACITY):
			self.mining = True
			if self.mine_block(block):
				self.chain.add_new_block(block)
				self.broadcast_block(block)
			self.cur_block = Block(block.index + 1, block.hash)

	def mine_block(self, block):
		block.nonce = randint(0, 4294967296)
		while (self.mining == True):
			if (block.myHash()[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY):
				block.hash = block.myHash()
				self.mining == False
				return True
			block.nonce += 1
		return False


	def broadcast_block(self, block):
		message = block.to_dict_hashed()
		message_json = json.dumps(message)
		for node in self.ring:
			if node['id'] == self.id:
				continue
			requests.post(node['address'] + "/block/receive", data = message_json, headers = headers)

	def valid_proof(self, block):
		if block.myHash == block.hash and block.hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY:
			return True
		return False

	def validate_block(self, index, previous_hash, timestamp, nonce, listOfTransactions, hash):
		if (self.mining == False):
			return True #We ignore simultaneous mined blocks, we will need concencus but we leave it for later
		self.mining = False
		cur_block = self.chain.cur_block()
		block = Block(index, previous_hash)
		block.time = timestamp
		block.nonce = nonce
		block.listOfTransactions = listOfTransactions
		list.hash = hash
		if self.valid_proof(block) and cur_block.hash == block.previousHash:
			self.chain.add_new_block(block)
			return True
		return False # Here we do concencus
	
	
	#concencus functions

	def validate_chain(self, chain):
		validation = True
		new_chain = []
		for block in chain:
			new_block = Block(block['index'], block['previous_hash'])
			new_block.timestamp = block['timestamp']
			new_block.nonce = block['nonce']
			new_block.listOfTransactions = block['transactions']
			new_block.hash = block['hash']
			if (new_block.index == 0):
				new_chain.append(new_block)
				continue
			if (self.valid_proof(new_block) and new_chain[-1].hash == new_block.previousHash):
				new_chain.append(new_block)
			else:
				validation = False
				break
		if (validation == True):
			self.chain = new_chain
		return validation


	def resolve_conflicts(self):
		#resolve correct chain
		current_length = len(self.chain.chain)
		for node in self.ring:
			if node['id'] == self.id:
				continue
			data = requests.get(node['address'] + '/blockchain/send').json()
			new_chain = data['blockchain']
			new_length = len(new_chain)
			if (new_length > current_length):
				if self.validate_chain(new_chain):
					current_length = len(self.chain.chain)