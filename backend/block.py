from transaction import Transaction
from Crypto.Hash import SHA256

from time import time
import json



class Block:
	def __init__(self, index, previousHash, nonce):
		##set
		self.index = index
		self.previousHash = previousHash
		self.timestamp = time()
		self.nonce = nonce
		self.listOfTransactions = []
		self.hash = self.myHash()
	
	def myHash(self):
		#calculate self.hash
		block = {'index': self.index,
		        'previous_hash': self.previousHash, 
                'timestamp': self.timestamp,
                'nonce': self.nonce,
                'transactions': self.listOfTransactions,
				}
		hash = SHA256.new(data = json.dumps(block).encode()).hexdigest()
		return hash


	def add_transaction(self, transaction):
		#add a transaction to the block
		self.listOfTransactions.append(transaction)

if __name__ == "__main__":
	block = Block(1,0,1)
	while (block.hash[:3] != '000'):
		block.nonce += 1
		block.hash = block.myHash()
		print(block.hash[:3])