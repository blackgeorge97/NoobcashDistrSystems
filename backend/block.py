from transaction import Transaction
from wallet import wallet
from Crypto.Hash import SHA256
from collections import OrderedDict
from time import time
import json



class Block:
	def __init__(self, index, previousHash):
		##set
		self.index = index
		self.previousHash = previousHash
		self.timestamp = time()
		self.nonce = 0
		self.listOfTransactions = []
		self.hash = self.myHash()

	def to_dict(self):
		block_dict = OrderedDict({
			'index' : self.index,
			'previous_hash': self.previousHash, 
            'timestamp': self.timestamp,
            'nonce': self.nonce,
			'transactions' : self.listOfTransactions
		})
		return block_dict

	def to_dict_hashed(self):
		block_dict = OrderedDict({
			'index' : self.index,
			'previous_hash': self.previousHash, 
            'timestamp': self.timestamp,
            'nonce': self.nonce,
			'transactions' : self.listOfTransactions,
			'hash' : self.hash
		})
		return block_dict
	
	def myHash(self):
		#calculate self.hash
		block = self.to_dict() 
		hash = SHA256.new(data = json.dumps(block).encode()).hexdigest()
		return hash


	def add_transaction(self, transaction):
		#add a transaction to the block
		self.listOfTransactions.append(transaction)



if __name__ == "__main__":
	block = Block(1,0)
	tran = Transaction(1, 2, 100, [])
	wallet = wallet()
	tran.Signature = tran.sign_transaction(wallet.private_key)
	block.add_transaction(tran.to_dict_signed())
	json_block = json.dumps(block.to_dict())
	print(json_block)