import json
from os import path

from django.test import TestCase, Client
from eth_account import Account, messages
from humps import decamelize
import pytest
from siwe.siwe import SiweMessage, ValidationError


BASE_TESTS = path.join("examples", "notepad", "siwe", "test")
with open(path.join(BASE_TESTS, "parsing_positive.json"), "r") as f:
    parsing_positive = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "parsing_negative.json"), "r") as f:
    parsing_negative = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "validation_negative.json"), "r") as f:
    validation_negative = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "validation_positive.json"), "r") as f:
    validation_positive = decamelize(json.load(fp=f))


class ApiTests(TestCase):

    def test_nonce(self):
        nonce_response = self.client.get('/api/auth/nonce')
        self.assertEqual(nonce_response.status_code, 200)
        nonce_content = json.loads(nonce_response.content)
        self.assertTrue('nonce' in nonce_content)


class SigningClientApiTest(TestCase):
    account = None
    
    def setUp(self):
        self.account = Account.create()

    def getNonce(self):
        nonce_response = self.client.get('/api/auth/nonce')
        nonce_content = json.loads(nonce_response.content)
        return nonce_content['nonce']

    def test_fails_without_nonce(self):
        # todo: same as below but without nonce
        pass 

    def test_message_round_trip(self):
        for test_name, test in parsing_positive.items():
            message = SiweMessage(test["fields"])
            message.address = self.account.address

            nonce = self.getNonce()
            message.nonce = nonce

            message_obj = {}
            for slot in message.__slots__:
                slotvalue = getattr(message, slot, None)
                if slotvalue is not None:
                    message_obj[slot] = slotvalue

            signature = self.account.sign_message(
                messages.encode_defunct(text=message.prepare_message())
            ).signature

            headers = {
                'content_type': 'application/json',
            }

            sig = signature.hex()
            loginAttemptResponse = self.client.post("/api/auth/login", {
                'message': message_obj,
                'signature': sig
            }, **headers)
            

            print('loginAttemptResponse', loginAttemptResponse)
            
            # fails because of infura key access denied
            # requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://mainnet.infura.io/v3/69bbfab4edd94ae0ae6a78d63f908d42
