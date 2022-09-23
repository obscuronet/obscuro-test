import os, json
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=False)

        # deploy the contract and dump out the abi
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f:
            json.dump(storage.abi, f)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.js')
        args = []
        args.extend(['-u', '%s' % network.connection_url(web_socket=True)])
        args.extend(['-a', '%s' % storage.contract_address])
        args.extend(['-b', '%s' % abi_path])
        args.extend(['-p', '%s' % Properties().account2pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)

        # perform some transactions
        for i in range(0, 5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)

        # check and assert
        self.waitForGrep(file=stdout, expr='args.*value', condition='== 5', timeout=20)
        self.assertLineCount(file=stdout, expr='args.*value', condition='== 5')
