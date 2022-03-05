import block
import wallet

MINING_DIFFICULTY = 1

class node:
	def __init__(self):
		self.NBC=100;
		##set

		self.chain
		self.current_id_count
		self.NBCs
		self.wallet

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


	def create_transaction(sender, receiver, signature):
		#remember to broadcast it
		return


	def broadcast_transaction():
		return



	def validdate_transaction():
		#use of signature and NBCs balance
		return


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