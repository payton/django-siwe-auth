import json
from os import path

import django.conf as conf
from django.test import TestCase, Client
from eth_account import Account, messages
from humps import decamelize
from siwe.siwe import SiweMessage, ValidationError
from siwe_auth.models import Nonce

# override settings for test
conf.settings.CREATE_GROUPS_ON_AUTHN = False
conf.settings.CREATE_ENS_PROFILE_ON_AUTHN = False

BASE_TESTS = path.join("examples", "notepad", "siwe", "test")
with open(path.join(BASE_TESTS, "parsing_positive.json"), "r") as f:
    parsing_positive = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "parsing_negative.json"), "r") as f:
    parsing_negative = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "validation_negative.json"), "r") as f:
    validation_negative = decamelize(json.load(fp=f))
with open(path.join(BASE_TESTS, "validation_positive.json"), "r") as f:
    validation_positive = decamelize(json.load(fp=f))

NONCE_ENDPOINT = '/api/auth/nonce'
LOGIN_ENDPOINT = '/api/auth/login'

class ApiTests(TestCase):

    def test_nonce(self):
        nonce_response = self.client.get(NONCE_ENDPOINT)
        self.assertEqual(nonce_response.status_code, 200)
        nonce_content = json.loads(nonce_response.content)
        self.assertTrue('nonce' in nonce_content)


class SigningClientApiTest(TestCase):
    account = None
    
    def setUp(self):
        self.account = Account.create()

    def getNonce(self):
        nonce_response = self.client.get(NONCE_ENDPOINT)
        nonce_content = json.loads(nonce_response.content)
        return nonce_content['nonce']

    def test_fails_without_nonce(self):
        for test_name, test in parsing_positive.items():
            message = SiweMessage(test['fields'])
            message.address = self.account.address

            # Convert SIWE message into dictionary for body of login HTTP request
            message_obj = {}
            for slot in message.__slots__:
                slotvalue = getattr(message, slot, None)
                if slotvalue is not None:
                    message_obj[slot] = slotvalue

            # Sign SIWE message with test Ethereum account
            signature = self.account.sign_message(
                messages.encode_defunct(text=message.prepare_message())
            ).signature

            headers = {
                'content_type': 'application/json',
            }

            # Assert that missing nonce fails login request
            sig = signature.hex()
            with self.assertRaises(Nonce.DoesNotExist):
                loginAttemptResponse = self.client.post(LOGIN_ENDPOINT, {
                    'message': message_obj,
                    'signature': sig
                }, **headers)

    def test_message_round_trip(self):
        for test_name, test in parsing_positive.items():
            message = SiweMessage(test['fields'])
            message.address = self.account.address

            # Add nonce to SIWE message
            nonce = self.getNonce()
            message.nonce = nonce

            # Convert SIWE message into dictionary for body of login HTTP request
            message_obj = {}
            for slot in message.__slots__:
                slotvalue = getattr(message, slot, None)
                if slotvalue is not None:
                    message_obj[slot] = slotvalue

            # Sign SIWE message with test Ethereum account
            signature = self.account.sign_message(
                messages.encode_defunct(text=message.prepare_message())
            ).signature

            headers = {
                'content_type': 'application/json',
            }

            # Assert that login request with valid nonce returns a 200
            sig = signature.hex()
            loginAttemptResponse = self.client.post(LOGIN_ENDPOINT, {
                'message': message_obj,
                'signature': sig
            }, **headers)
            
            self.assertEqual(loginAttemptResponse.status_code, 200)
