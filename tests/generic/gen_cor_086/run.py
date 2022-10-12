import os, time
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self)
        web3_2, account2 = network.connect_account2(self)
        web3_3, account3 = network.connect_account3(self)

        # deploy the contract and dump out the abi
        storage = KeyStorage(self, web3_1)
        storage.deploy(network, account1)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'listener.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', ws_url])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--filter_address', '%s' % account2.address])
        args.extend(['--filter_key', 'k2'])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        contract_1 = storage.contract
        contract_2 = web3_2.eth.contract(address=storage.contract_address, abi=storage.abi)
        contract_3 = web3_3.eth.contract(address=storage.contract_address, abi=storage.abi)
        network.transact(self, web3_1, contract_1.functions.setItem('k1', 1), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('foo', 2), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('bar', 3), account1, storage.GAS)
        network.transact(self, web3_2, contract_2.functions.setItem('k2', 4), account2, storage.GAS)
        network.transact(self, web3_3, contract_3.functions.setItem('r1', 5), account2, storage.GAS)
        network.transact(self, web3_3, contract_3.functions.setItem('r2', 6), account3, storage.GAS)

        # wait and validate
        self.waitForGrep(file=stdout, expr='stored value = [0-9]$', condition='== 3', timeout=20)
        expr_list = ['ItemSet3, stored value = 4', 'ItemSet1, stored value = 4', ' ItemSet1, stored value = 5']
        self.assertOrderedGrep(file=stdout, exprList=expr_list)
