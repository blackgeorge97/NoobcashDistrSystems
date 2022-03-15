import binascii

import Crypto
import Crypto.Random as Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import transaction

class wallet:

	def __init__(self):
		##set

		self.private_key, self.public_key = self.generate_keys()
		self.address = self.public_key
		self.utxos = []

	def generate_keys(self):
		random_number = Random.new().read
		key = RSA.generate(1024, random_number)
		private_key = key.exportKey(format='DER')
		public_key = key.publickey().exportKey(format='DER')
		return binascii.hexlify(private_key).decode('utf8'), binascii.hexlify(public_key).decode('utf8')


	def balance(self):
		bal = 0
		for tran in self.utxos:
			bal += tran['amount']
		return bal

if __name__ == "__main__":
	wallet = wallet()
	print(wallet.private_key)