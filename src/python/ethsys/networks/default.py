from web3 import Web3
from collections import OrderedDict
from pysys.constants import *
from ethsys.utils.properties import Properties


class Default:
    """A default node giving access to an underlying network."""
    HOST = 'http://127.0.0.1'
    WS_HOST = 'ws://127.0.0.1'
    PORT = 8545
    WS_PORT = 8546
    CONNECTIONS = OrderedDict()

    @classmethod
    def chain_id(cls): return None

    @classmethod
    def connect(cls, test, private_key, web_socket=False):
        key = (cls.__name__, private_key, web_socket)

        if key in cls.CONNECTIONS:
            web3, _ = cls.CONNECTIONS[key]
            if not web3.isConnected():
                test.log.info('Re-adding connection for %s' % private_key)
                cls.CONNECTIONS[key] = cls.connection(test, private_key, web_socket)
        else:
            test.log.info('Adding new connection for %s' % private_key)
            cls.CONNECTIONS[key] = cls.connection(test, private_key, web_socket)
        return cls.CONNECTIONS[key]

    @classmethod
    def connection(cls, test, private_key, web_socket):
        provider = Web3.HTTPProvider if not web_socket else Web3.WebsocketProvider
        port = cls.PORT if not web_socket else cls.WS_PORT
        host = cls.HOST if not web_socket else cls.WS_HOST

        test.log.info('Connecting to network on %s:%d' % (host, port))
        web3 = Web3(provider('%s:%d' % (host, port)))
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account

    @classmethod
    def connect_account1(cls, test, web_socket=False):
        return cls.connect(test, Properties().account1pk(), web_socket)

    @classmethod    
    def connect_account2(cls, test, web_socket=False):
        return cls.connect(test, Properties().account2pk(), web_socket)

    @classmethod
    def connect_account3(cls, test, web_socket=False):
        return cls.connect(test, Properties().account3pk(), web_socket)

    @classmethod
    def connect_game_user(cls, test, web_socket=False):
        return cls.connect(test, Properties().gameuserpk(), web_socket)

    @classmethod
    def transact(cls, test, web3, target, account, gas):
        tx_sign = cls.build_transaction(test, web3, target, account, gas)
        tx_hash = cls.send_transaction(test, web3, tx_sign)
        tx_recp = cls.wait_for_transaction(test, web3, tx_hash)
        return tx_recp

    @classmethod
    def build_transaction(cls, test, web3, target, account, gas):
        build_tx = target.buildTransaction(
            {
                'nonce': web3.eth.get_transaction_count(account.address),
                'gasPrice': 21000,
                'gas': gas,
                'chainId': web3.eth.chain_id
            }
        )
        signed_tx = account.sign_transaction(build_tx)
        return signed_tx

    @classmethod
    def send_transaction(cls, test, web3, signed_tx):
        tx_hash = None
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            test.log.error('Error sending raw transaction %s' % e)
            test.addOutcome(BLOCKED, abortOnError=True)
        test.log.info('Transaction sent with hash %s' % tx_hash.hex())
        return tx_hash

    @classmethod
    def wait_for_transaction(cls, test, web3, tx_hash):
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            test.log.info('Transaction receipt block hash %s' % tx_receipt.blockHash.hex())
        else:
            test.log.error('Transaction receipt failed')
            test.log.error('Full receipt: %s' % tx_receipt)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_receipt
