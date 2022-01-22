from abc import ABC, abstractmethod
from web3 import HTTPProvider


class GroupManager(ABC):
    @abstractmethod
    def __init__(self, config: dict):
        """
        GroupManager initialization function.
        :param config: Dictionary for passing in any dependencies such as contract address or list of valid addresses.
        """
        pass

    @abstractmethod
    def is_member(self, ethereum_address: str, provider: HTTPProvider) -> bool:
        """
        Membership function to identify if a given ethereum address is part of this class' group.
        :param provider: Web3 provider to use for membership check.
        :param ethereum_address: Address to check membership of.
        :return: True if address is a member else False
        """
        pass
