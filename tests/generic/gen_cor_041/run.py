from ethsys.basetest import EthereumTest
from ethsys.contracts.guesser.guesser_constructor import GuesserConstructor
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        guesser = GuesserConstructor(self, web3, 0, 100)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess() == guesser.secret)
