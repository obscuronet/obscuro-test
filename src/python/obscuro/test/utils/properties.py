import getpass, configparser, secrets
from pysys.constants import *


class Properties:
    """Used as a holding class for properties."""

    def __init__(self):
        self.default_config = configparser.ConfigParser()
        self.default_config.read(filenames=os.path.join(PROJECT.root, '.default.properties'))

        self.user_config = configparser.ConfigParser()
        file = os.path.join(PROJECT.root, '.'+getpass.getuser()+'.properties')
        if os.path.exists(file):
            self.user_config.read(filenames=file)

    def get(self, section, option):
        if self.user_config.has_option(section, option):
            return self.user_config.get(section, option)
        else:
            return self.default_config.get(section, option)

    # generally used
    def account1pk(self):
        return self.get('all', 'Account1PK')

    def account2pk(self):
        return self.get('all', 'Account2PK')

    def account3pk(self):
        return self.get('all', 'Account3PK')

    def gameuserpk(self):
        return self.get('all', 'GameUserPK')

    # obscuro specific properties
    def faucet_url(self, key):
        return self.get(key, 'FaucetURL')

    def management_bridge_address(self, key):
        return self.get(key, 'ManagementBridgeAddress')

    def guessing_game_address(self, key):
        return self.get(key, 'GuessingGameAddress')

    def distro_account_pk(self, key):
        return self.get(key, 'DistroAccountPK')

    def l1_funded_account_pk(self, key):
        return self.get(key, 'L1FundedAccountPK')

    def l1_hoc_token_address(self, key):
        return self.get(key, 'L1TokenHOCContractAddress')

    def l1_poc_token_address(self, key):
        return self.get(key, 'L1TokenPOCContractAddress')

    def l2_funded_account_pk(self, key):
        return self.get(key, 'L2FundedAccountPK')

    def l2_hoc_token_address(self, key):
        return self.get(key, 'L2TokenHOCContractAddress')

    def l2_poc_token_address(self, key):
        return self.get(key, 'L2TokenPOCContractAddress')

    # infura related
    def infuraProjectID(self):
        return self.get('ropsten', 'ProjectID')