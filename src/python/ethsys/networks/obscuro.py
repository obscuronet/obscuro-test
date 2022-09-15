import requests, time, json
from web3 import Web3
from collections import OrderedDict
from pysys.constants import *
from ethsys.networks.default import Default
from ethsys.networks.geth import Geth
from eth_account.messages import encode_defunct


class ObscuroL1(Geth):
    HOST = 'http://testnet-gethnetwork.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9000


class ObscuroL1Dev(Geth):
    HOST = 'http://dev-testnet-gethnetwork.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9001


class ObscuroL1Local(Geth):
    HOST = 'http://127.0.0.1'
    PORT = 8025
    WS_PORT = 9002


class Obscuro(Default):
    """The Obscuro wallet extension giving access to the underlying network."""
    HOST = 'http://127.0.0.1'
    WS_HOST = 'ws://127.0.0.1'
    PORT = 3000
    WS_PORT = 3001
    HTTP_CONNECTIONS = OrderedDict()

    @classmethod
    def chain_id(cls):
        return 777

    @classmethod
    def connection(cls, private_key, web_socket):
        provider = Web3.HTTPProvider if not web_socket else Web3.WebsocketProvider
        port = cls.PORT if not web_socket else cls.WS_PORT
        host = cls.HOST if not web_socket else cls.WS_HOST

        web3 = Web3(provider('%s:%d' % (host, port)))
        account = web3.eth.account.privateKeyToAccount(private_key)
        cls.__generate_viewing_key(web3, cls.HOST, cls.PORT, account, private_key)
        return web3, account

    @classmethod
    def wait_for_transaction(cls, test, web3, tx_hash):
        start = time.time()
        tx_receipt = None
        while tx_receipt is None:
            if (time.time() - start) > 180:
                test.log.error('Timed out waiting for transaction receipt ... aborting')
                test.addOutcome(TIMEDOUT, abortOnError=True)

            try:
                tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                time.sleep(1)

        if tx_receipt.status == 1:
            test.log.info('Transaction complete gasUsed=%d' % tx_receipt.gasUsed)
            test.log.info('Transaction receipt block hash %s' % tx_receipt.blockHash.hex())
        else:
            test.log.error('Transaction receipt failed')
            test.log.error('Full receipt: %s' % tx_receipt)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_receipt

    @classmethod
    def __generate_viewing_key(cls, web3, host, port, account, private_key):
        # generate a viewing key for this account, sign and post it to the wallet extension
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {"address": account.address}
        response = requests.post('%s:%d/generateviewingkey/' % (host, port), data=json.dumps(data), headers=headers)
        signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)

        data = {"signature": signed_msg.signature.hex(), "address": account.address}
        requests.post('%s:%d/submitviewingkey/' % (host, port), data=json.dumps(data), headers=headers)
