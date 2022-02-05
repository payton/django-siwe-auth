from abc import abstractmethod
import logging
from typing import Callable

from siwe_auth.custom_groups.group_manager import GroupManager

from web3 import Web3, HTTPProvider


class ERC1155Manager(GroupManager):

    contract: str
    token_id: int
    abi = [
        {
            "constant": False,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_id", "type": "uint256"},
            ],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "type": "function",
        }
    ]

    def __init__(self, config: dict):
        if "contract" not in config:
            raise ValueError(
                "ERC1155 Owner Manager config is missing contract attribute."
            )
        if "token_id" not in config:
            raise ValueError(
                "ERC1155 Owner Manager config is missing token id attribute."
            )
        self.contract = config["contract"]
        self.token_id = int(config["token_id"])

    def _is_member(
        self,
        ethereum_address: str,
        provider: HTTPProvider,
        expression: Callable[[str], bool],
    ):
        w3 = Web3(provider)
        contract = w3.eth.contract(
            address=Web3.toChecksumAddress(self.contract.lower()), abi=self.abi
        )
        balance = contract.functions.balanceOf(
            _owner=Web3.toChecksumAddress(ethereum_address.lower()),
            _id=self.token_id,
        ).call()
        return expression(balance)

    @abstractmethod
    def is_member(self, wallet: object, provider: HTTPProvider) -> bool:
        pass


class ERC1155OwnerManager(ERC1155Manager):
    def is_member(self, wallet: object, provider: HTTPProvider) -> bool:
        if not self._valid_wallet(wallet=wallet):
            return False
        try:
            return self._is_member(
                ethereum_address=wallet.ethereum_address,
                provider=provider,
                expression=lambda x: x > 0,
            )
        except ValueError:
            logging.error(
                f"Unable to verify membership of invalid address: {wallet.ethereum_address}"
            )
        return False
