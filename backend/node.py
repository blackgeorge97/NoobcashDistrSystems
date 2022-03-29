from ensurepip import bootstrap
import queue
from block import Block
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction
import json
import requests
from random import randint
import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict

MINING_DIFFICULTY = 4
CAPACITY = 1
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class node:
	def __init__(self, bootstrap, ip, port, n, bootstrap_ip, bootstrap_port):
		##set
		self.ready = False
		self.max_nodes = n
		self.current_id_count = 0
		self.chain = Blockchain()
		self.wallet = wallet()
		self.utxos_per_node = {}
		self.utxos_lock = Lock()
		self.tran_queue = []
		self.used_queue = []
		self.tran_queue_lock = Lock()
		self.mining = False
		self.mining_lock = Lock()
		self.handling = False
		self.handling_lock = Lock()
		self.ring = [] #here we store information for every node, as its id, its address (ip:port) its public key and its balance
		self.id = 0
		addr = ip + ':' + port
		temp_node = {'id' : self.current_id_count, 'address' : addr, 'public_key' : self.wallet.public_key}
		self.utxos_per_node[self.wallet.public_key] = []
		#test values start
		self.tran_count = 0
		self.added_blocks = 0
		self.total_sum_time = 0
		self.last_block_time = 0
		self.start_time = 0
		self.start_mine_time = 0
		self.start_progress = False
        #test values end
		self.ring.append(temp_node) 
		if (bootstrap):
			block = Block(0, 1)
			new_tran = Transaction(0, self.wallet.public_key, 100*n, [])
			out =  OrderedDict({
				'id' : new_tran.transaction_id,
				'receiver' : new_tran.receiver_address,
				'amount' : new_tran.amount
		    })
			self.utxos_per_node[out['receiver']].append(out)
			self.wallet.utxos.append(out)
			new_tran.transaction_outputs.append(out)
			block.add_transaction(new_tran.to_dict_signed())
			block.hash = block.myHash()
			self.chain.chain.append(block)
			self.cur_block  = Block(block.index + 1, block.hash)
		else:
			message = {'address' : addr, 'public_key' : self.wallet.public_key}
			message_json = json.dumps(message)
			url = 'http://' + bootstrap_ip + ':' + bootstrap_port + '/network/register'
			executor = ThreadPoolExecutor(max_workers=1)
			executor.submit(post_function, url, message_json)

	 		
	def receive_reg_info(self, ring, index, timestamp, previous_hash, nonce, listOfTransactions, hash):
		self.ring = ring
		for node in self.ring:
			if node['public_key'] == self.wallet.public_key:
				self.id = node['id']
			self.utxos_per_node[node['public_key']] = []
		self.max_nodes = len(self.ring)
		block = Block(index, previous_hash)
		block.timestamp = timestamp
		block.nonce = nonce
		block.listOfTransactions = listOfTransactions
		block.hash = hash
		self.chain.chain.append(block)
		output = listOfTransactions[0]['outputs'][0]
		self.utxos_per_node[output['receiver']].append(output)
		self.cur_block  = Block(block.index + 1, block.hash)

	def register_node_to_ring(self, address, public_key):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		self.current_id_count += 1
		temp_node = {'id' : self.current_id_count, 'address' : address, 'public_key' : public_key}
		self.ring.append(temp_node)
		self.utxos_per_node[public_key] = []
		if self.current_id_count + 1 == self.max_nodes:
			message = {'ring' : self.ring, 'genesis_block' : self.chain.cur_block().to_dict_hashed()}
			message_json = json.dumps(message)
			for node in self.ring:
				if not node['id'] == self.id:
					requests.post('http://' + node['address'] + "/network/receive", data = message_json, headers = headers)
			for node in self.ring:
				if not node['id'] == self.id:
					self.create_transaction(self.wallet.public_key, node['public_key'], 100)
			for node in self.ring:
				if not node['id'] == self.id:
					response = requests.get('http://' + node['address'] + '/network/ready').json()
			self.ready = True
			print("Network ready")
			return True
		return False

	def queue_handler(self):
		self.tran_queue_lock.acquire()
		if len(self.tran_queue) == 0 or len(self.cur_block.listOfTransactions) == CAPACITY:
			self.tran_queue_lock.release()
			return
		tran = self.tran_queue.pop(0)
		self.used_queue.append(tran)
		self.add_transaction_to_block(tran)


	def create_transaction(self, sender, receiver, amount):
		#remember to broadcast it
		total_sum = 0
		used_tran = []
		self.utxos_lock.acquire()
		for utxo in self.utxos_per_node[sender]:
			total_sum += utxo['amount']
			used_tran.append(utxo)
			if(total_sum >= amount):
				break
		if (total_sum < amount):
			print("Not enough nbc")
			self.utxos_lock.release()
			return False
		for used in used_tran:
			self.utxos_per_node[sender].remove(used)
			self.wallet.utxos.remove(used)
		new_tran = Transaction(sender, receiver, amount, used_tran)
		outputs = []
		out1 = OrderedDict({
			'id' : new_tran.transaction_id,
			'receiver' : new_tran.receiver_address,
			'amount' : new_tran.amount
		})
		outputs.append(out1)
		self.utxos_per_node[receiver].append(out1)
		if (total_sum > amount):
			out2 = OrderedDict({
				'id' : new_tran.transaction_id,
				'receiver' : new_tran.sender_address,
				'amount' : total_sum - new_tran.amount
			})
			outputs.append(out2)
			self.utxos_per_node[sender].append(out2)
			self.wallet.utxos.append(out2)
		self.utxos_lock.release()
		new_tran.transaction_outputs = outputs
		new_tran.Signature = new_tran.sign_transaction(self.wallet.private_key)
		self.tran_queue_lock.acquire()
		#test
		if self.start_progress == False and self.ready == True:
			self.start_progress = True
			self.start_time = time.time()
			self.tran_count = 0
		self.tran_count += 1
		#test
		self.tran_queue.append(new_tran.to_dict_signed())
		self.tran_queue_lock.release()
		self.broadcast_transaction(new_tran)
		return True

	def broadcast_transaction(self, tran):
		message = tran.to_dict_signed()
		message_json = json.dumps(message)
		with ThreadPoolExecutor(max_workers=len(self.ring) + 1) as executor:
			for node in self.ring:
				if node['id'] == self.id:
					continue
				url = 'http://' + node['address'] + '/transaction/receive'
				executor.submit(post_function, url, message_json)
			executor.submit(self.queue_handler)


	def validate_transaction(self, transaction, signature, public_key):
		#use of signature and NBCs balance
		for input in transaction.transaction_inputs:
			if input not in self.utxos_per_node[transaction.sender_address]:
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
		self.utxos_lock.acquire()
		for i in input:
			self.utxos_per_node[sender].remove(i)
		for i in output:
			self.utxos_per_node[i['receiver']].append(i)
			if (i['receiver'] == self.wallet.public_key):
				self.wallet.utxos.append(i)
		self.utxos_lock.release()
		self.tran_queue_lock.acquire()
		#test
		if self.start_progress == False and self.ready == True:
			self.start_progress = True
			self.start_time = time.time()
			self.tran_count = 0
		self.tran_count += 1
		#test
		self.tran_queue.append(new_tran.to_dict_signed())
		self.tran_queue_lock.release()
		self.queue_handler()
		return True
	
	def view_transactions(self):
		return self.chain.cur_block().listOfTransactions

	def add_transaction_to_block(self, tran):
		#if enough transactions  mine
		block = self.cur_block
		block.add_transaction(tran)
		self.tran_queue_lock.release()
		if (len(block.listOfTransactions) == CAPACITY):
			self.start_mine_time = time.time()
			self.mining_lock.acquire()
			self.mining = True
			self.mining_lock.release()
			if self.mine_block(block):
				#test
				self.added_blocks += 1
				self.total_sum_time += time.time() - self.start_mine_time
				self.last_block_time = time.time()
				#test
				self.chain.add_new_block(block)
				self.mining_lock.release()
				self.broadcast_block(block)
			self.cur_block = Block(self.chain.cur_block().index + 1, self.chain.cur_block().hash)
		self.queue_handler()

	def mine_block(self, block):
		block.nonce = randint(0, 4294967296)
		while True:
			self.mining_lock.acquire()
			if self.mining == False:
				self.mining_lock.release()
				return False
			if (block.myHash()[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY):
				block.hash = block.myHash()
				self.tran_queue_lock.acquire()
				self.used_queue = []
				self.tran_queue_lock.release()
				self.mining = False
				return True
			self.mining_lock.release()
			block.nonce += 1


	def broadcast_block(self, block):
		message = {'block' : block.to_dict_hashed(), 'tran_queue' : self.tran_queue}
		message_json = json.dumps(message)
		with ThreadPoolExecutor(max_workers=len(self.ring)) as executor:
			for node in self.ring:
				if node['id'] == self.id:
					continue
				url = 'http://' + node['address'] + '/block/receive'
				executor.submit(post_function, url, message_json)
	

	def valid_proof(self, block):
		if block.myHash() == block.hash and block.hash[:MINING_DIFFICULTY] == '0' * MINING_DIFFICULTY:
			return True
		return False

	def validate_block(self, index, previous_hash, timestamp, nonce, listOfTransactions, hash, queue):
		self.mining_lock.acquire()
		if (self.mining == False):
			self.mining_lock.release()
			return True
		self.mining = False
		cur_block = self.chain.cur_block()
		block = Block(index, previous_hash)
		block.timestamp = timestamp
		block.nonce = nonce
		block.listOfTransactions = listOfTransactions
		block.hash = hash
		if self.valid_proof(block) and cur_block.hash == block.previousHash:
			#test
			self.added_blocks += 1
			self.total_sum_time += time.time() - self.start_mine_time
			self.last_block_time = time.time()
			#test
			self.chain.add_new_block(block)
			self.tran_queue_lock.acquire()
			for tran in block.listOfTransactions:
				if tran in self.tran_queue:
					self.tran_queue.remove(tran)
				elif tran in self.used_queue:
					self.used_queue.remove(tran)
			self.tran_queue = self.used_queue + self.tran_queue
			self.used_queue = []
			self.tran_queue_lock.release()
			self.mining_lock.release()
			return True
		self.resolve_conflicts() # Here we do concencus
		return False 
	
	
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
			return (new_chain, True)
		return ([], False)


	def resolve_conflicts(self):
		#resolve correct chain
		current_length = len(self.chain.chain)
		for node in self.ring:
			if node['id'] == self.id:
				continue
			data = requests.get('http://' + node['address'] + '/blockchain/send').json()
			new_chain = data['blockchain']
			new_queue = data['tran_queue']
			new_used_queue = data['used_queue']
			new_length = len(new_chain)
			if (new_length >= current_length):
				(chain, validation) = self.validate_chain(new_chain)
				if validation:
					self.chain.chain = chain
					self.tran_queue_lock.acquire()
					self.tran_queue = self.used_queue + self.tran_queue
					for tran in new_queue:
						if tran in self.tran_queue:
							self.tran_queue.remove(tran)
					for tran in new_used_queue:
						if tran in self.tran_queue:
							self.tran_queue.remove(tran)
					for block in chain:
						if len(self.tran_queue) == 0:
							break
						for tran in block.listOfTransactions:
							if tran in self.tran_queue:
								self.tran_queue.remove(tran)
					self.tran_queue = self.tran_queue + new_used_queue + new_queue
					self.used_queue = []
					self.tran_queue_lock.release()
					current_length = len(self.chain.chain)
		self.mining_lock.release()


def post_function(url, message):
	requests.post(url, data = message, headers = headers)