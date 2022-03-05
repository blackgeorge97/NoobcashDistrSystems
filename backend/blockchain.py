import block

class Blockchain():
    def __init__(self):
        self.chain = []

    def append_block(self, Block: block):
        self.chain.append(block)