from datetime import datetime
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError

from web3 import Web3


def validate_ethereum_address(value):
    if not Web3.isChecksumAddress(value):
        raise ValidationError


class WalletManager(BaseUserManager):
    def create_user(self, ethereum_address: str):
        """
        Creates and saves a User with the given ethereum address.
        """
        if not ethereum_address:
            raise ValueError("Users must have an ethereum address")

        wallet = self.model()
        wallet.ethereum_address = ethereum_address

        wallet.save(using=self._db)
        return wallet

    def create_superuser(self, ethereum_address: str):
        """
        Creates and saves a superuser with the given ethereum address.
        """
        user = self.create_user(
            ethereum_address=ethereum_address,
        )
        user.set_unusable_password()
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Wallet(AbstractBaseUser, PermissionsMixin):
    # EIP-55 compliant: https://eips.ethereum.org/EIPS/eip-55
    ethereum_address = models.CharField(
        unique=True,
        primary_key=True,
        max_length=42,
        validators=[validate_ethereum_address],
    )
    ens_name = models.CharField(max_length=255, blank=True, null=True)
    ens_avatar = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField("datetime created", auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "ethereum_address"

    objects = WalletManager()

    def __str__(self):
        return self.ethereum_address

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Nonce(models.Model):
    value = models.CharField(max_length=24, primary_key=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return self.value
