from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):


        ##set
        self.sender_address
        self.receiver_address
        self.amount
        self.transaction_id
        self.transaction_inputs
        self.transaction_outputs
        self.Signature


    


    def to_dict(self):
        return
        

    def sign_transaction(self):
        #Sign transaction with private key
        return