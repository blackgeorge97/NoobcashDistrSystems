from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template
import wallet
import json


class Transaction:

    def __init__(self, sender_address, recipient_address, value, transaction_inputs):


        ##set
        self.sender_address = sender_address
        self.receiver_address = recipient_address
        self.amount = value
        self.transaction_inputs = transaction_inputs
        self.transaction_outputs = []
        self.Signature = ''
        self.transaction_id = self.hash_tran()


    
    def hash_tran(self):
        tran_dict = {
            'sender' : self.sender_address, 
		    'receiver' : self.receiver_address,  
		    'amount' : self.amount, 
            'inputs' : self.transaction_inputs
        }
        hash = SHA256.new(data = json.dumps(tran_dict).encode()).hexdigest()
        return hash


    def to_dict(self):
        tran_dict = OrderedDict({   
            'id' : self.transaction_id,
            'sender' : self.sender_address, 
		    'receiver' : self.receiver_address,  
		    'amount' : self.amount, 
            'inputs' : self.transaction_inputs, 
            'outputs' : self.transaction_outputs
        })
        return tran_dict

    def to_dict_signed(self):
        tran_dict = OrderedDict({   
            'id' : self.transaction_id,
            'sender' : self.sender_address, 
		    'receiver' : self.receiver_address,  
		    'amount' : self.amount, 
            'inputs' : self.transaction_inputs, 
            'outputs' : self.transaction_outputs,
            'signature' : self.Signature
        })
        return tran_dict
        

    def sign_transaction(self, sender_private_key):
        #Sign transaction with private key
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        tran_dict = json.dumps(self.to_dict()).encode()
        hash = SHA256.new(str(tran_dict).encode('utf8'))
        return binascii.hexlify(signer.sign(hash)).decode('utf8')
    
    def verify_signature(self, sender_public_key, signature):
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        tran_dict = json.dumps(self.to_dict()).encode()
        hash = SHA256.new(str(tran_dict).encode('utf8'))
        return verifier.verify(hash, binascii.unhexlify(signature))
        

if __name__ == "__main__":
    wallet = wallet.wallet()
    tran= Transaction(1, 2, 100, [])
    tran.Signature = tran.sign_transaction(wallet.private_key)
    print(tran.verify_signature(wallet.public_key, tran.Signature))