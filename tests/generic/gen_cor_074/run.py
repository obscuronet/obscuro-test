import os, json
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self)
        web3_2, account2 = network.connect_account2(self)
        web3_3, account3 = network.connect_account3(self)

        # deploy the contract and dump out the abi
        storage = KeyStorage(self, web3_1)
        storage.deploy(network, account1)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f:
            json.dump(storage.abi, f)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--filter_address', '%s' % account2.address])
        args.extend(['--filter_key', '%s' % 'r1'])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions
        contract_1 = storage.contract
        contract_2 = web3_2.eth.contract(address=storage.contract_address, abi=storage.abi)
        contract_3 = web3_3.eth.contract(address=storage.contract_address, abi=storage.abi)
        network.transact(self, web3_1, contract_1.functions.setItem('k1', 1), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('foo', 2), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('bar', 3), account1, storage.GAS)
        network.transact(self, web3_2, contract_2.functions.setItem('k2', 2), account2, storage.GAS)
        network.transact(self, web3_3, contract_3.functions.setItem('r1', 10), account3, storage.GAS)
        network.transact(self, web3_3, contract_3.functions.setItem('r2', 11), account3, storage.GAS)

        # wait and validate - filter on sender is account2.address
        self.waitForGrep(file=stdout, expr='Task1:', condition='== 1', timeout=10)
        self.assertGrep(file=stdout, expr='Task1: k1 1', contains=False)
        self.assertGrep(file=stdout, expr='Task1: k2 2')

        # wait and validate - filter on value 2 or 3
        self.waitForGrep(file=stdout, expr='Task2:', condition='== 3', timeout=10)
        self.assertOrderedGrep(file=stdout, exprList=['Task2: foo 2', 'Task2: bar 3', 'Task2: k2 2'])

        # wait and validate - filter on key is r1
        self.waitForGrep(file=stdout, expr='Task3:', condition='== 1', timeout=10)
        self.assertGrep(file=stdout, expr='Task3: 10')

