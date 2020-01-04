from functools import reduce
import hashlib as hl
import json
import requests

from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, [], '', 100, 0)
        # initializing our empty blockchain list
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.public_Key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]
    
    @chain.setter
    def chain(self, val):
        self.__chain = val
    
    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        
        try:
            with open('quonix_blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]   
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_open_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx ['recipient'], tx['signature'], tx['amount'])
                    updated_open_transactions.append(updated_transaction)
                self.__open_transactions = updated_open_transactions 
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass            
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('quonix_blockchain-{}.txt'.format(self.node_id), mode="w") as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions] , block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]    
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed!')


    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof
    

    def get_balance(self):
        if self.public_Key == None:
            return None
        participant = self.public_Key
        tx_sender = [[tx.amount for tx in block.transactions
                    if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount 
                            for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions
                    if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """Returns the last value of the current blockchain"""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Appends a new value as well as the last blockchain value to the blockchain

        Arguments:
            :amount: The amount of tokens sent in the tx(default = 1.0)
        """
        # transaction = {
        #     'sender':sender, 
        #     'recipient':recipient,
        #     'amount':amount,
        #     }
        if self.public_Key == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if not Wallet.verify_transaction(transaction):
            return False
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)     
            self.save_data()
            for node in self.__peer_nodes:
                url = '/http://{}/broadcast-transaction'.format(node)
                try:
                    response = requests.post(url, json={'sender', sender, 'recipient', recipient, 'signature', signature, 'amount', amount})
                    if response.status_code == 400 or if response.status_code == 500:
                        print('Transaction failed, needs resolving')
                        return False
                except requests.exceptions.ConnectionError
                    continue
            return True
        return False


    def mine_block(self):
        if self.public_Key == None: 
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,  
        #     'amount': MINING_REWARD
        # } 
        reward_transaction = Transaction('MINING', self.public_Key, '', MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, 
                      copied_transactions, proof) 
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block


    def add_peer_node(self, node):
        """Adds a peer node to the set.
        
        Arguments:
            node: the URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    
    def get_peer_nodes(self):
        return list(self.__peer_nodes)




