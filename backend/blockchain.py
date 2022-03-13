from block import Block
import json

class Blockchain():
    def __init__(self):
        self.chain = []
        self.cur_id = 0

    def add_new_block(self, block):
        self.cur_id += 1
        self.chain.append(block)

    def to_dict(self):
        chain_list = []
        for block in self.chain:
            chain_list.append(block.to_dict_hashed())
        return chain_list

    def cur_block(self):
        return self.chain[-1]