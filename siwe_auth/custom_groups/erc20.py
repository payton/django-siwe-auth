import logging

from siwe_auth.custom_groups.group_manager import GroupManager

from web3 import Web3, HTTPProvider


class ERC20OwnerManager(GroupManager):
    contract: str
    abi = [
        {
            "constant": False,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "type": "function",
        }
    ]

    def __init__(self, config: dict):
        if "contract" not in config:
            raise ValueError(
                "ERC20 Owner Manager config is missing contract attribute."
            )
        self.contract = config["contract"]

    def is_member(self, ethereum_address: str, provider: HTTPProvider) -> bool:
        try:
            w3 = Web3(provider)
            contract = w3.eth.contract(
                address=Web3.toChecksumAddress(self.contract.lower()), abi=self.abi
            )
            balance = contract.functions.balanceOf(
                _owner=Web3.toChecksumAddress(ethereum_address.lower())
            ).call()
            return balance > 0
        except ValueError:
            logging.error(
                f"Unable to verify membership of invalid address: {ethereum_address}"
            )

        return False
