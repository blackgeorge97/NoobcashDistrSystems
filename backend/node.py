from block import Block
from blockchain import Blockchain
from wallet import wallet
from transaction import Transaction

MINING_DIFFICULTY = 4

class node:
	def __init__(self, n):
		self.NBC=100;
		##set

		self.chain = Blockchain()
		self.current_id_count = 0
		self.NBCs = 100*n
		self.wallet = wallet()
		self.utxos_per_node = {}

		self.ring = []   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 




	def create_new_block():
		return

	def create_wallet():
		#create a wallet for this node, with a public key and a private key
		return

	def register_node_to_ring():
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
			return
		for used in used_tran:
            #print(i)
			self.utxos_per_nodes[sender].remove(used)
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
		
		new_tran.transaction_outputs = outputs
		new_tran.Signature = new_tran.sign_transaction(self.wallet.private_key)
		self.broadcast_transaction(new_tran)
		self.add_transaction_to_block(new_tran)
        

	def broadcast_transaction():
		return



	def validate_transaction(self, transaction, signature, public_key):
		#use of signature and NBCs balance
		if transaction.verify_signature(public_key, signature):
			return True
		return False
 

	def add_transaction_to_block():
		#if enough transactions  mine
		return



	def mine_block():
		return



	def broadcast_block():
		return



	def valid_proof(difficulty=MINING_DIFFICULTY): #def valid_proof(.., difficulty=MINING_DIFFICULTY):
		return




	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes
		return


	def resolve_conflicts(self):
		#resolve correct chain
		return