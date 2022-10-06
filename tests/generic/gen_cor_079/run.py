import os
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions on the storage contract
        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.storeItem(100), account, storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, storage.GAS)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value = [0-9]{1,3}$', condition='== 6', timeout=20)

        expr_list = []
        expr_list.append('Stored value = 0')
        expr_list.append('Stored value = 1')
        expr_list.append('Stored value = 2')
        expr_list.append('Stored value = 3')
        expr_list.append('Stored value = 4')
        expr_list.append('Stored value = 100')
        self.assertOrderedGrep(file=stdout, exprList=expr_list)

