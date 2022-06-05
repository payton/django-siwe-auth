import datetime

import pytz

from django.test import TestCase
from eth_account import Account

from siwe_auth.models import Wallet

class WalletTests(TestCase):

    def test_created(self):
        now = datetime.datetime.now(tz=pytz.UTC)
        account = Account.create()
        wallet = Wallet.objects.create(ethereum_address=account.address)
        diff = wallet.created - now
        self.assertTrue(diff < datetime.timedelta(seconds=1))
