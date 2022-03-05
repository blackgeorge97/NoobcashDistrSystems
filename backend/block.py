
from blockchain import Blockchain
from transaction import Transaction



class Block:
	def __init__(self):
		##set
		self.index
		self.previousHash
		self.timestamp
		self.hash
		self.nonce
		self.listOfTransactions
	
	def myHash():
		#calculate self.hash
		return


	def add_transaction(self, transaction, blockchain):
		#add a transaction to the block
		return