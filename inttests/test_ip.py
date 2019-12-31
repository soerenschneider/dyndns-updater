import os
import logging

from unittest import TestCase
from notifier import UpdateNotifier

MOUNTEBANK = os.getenv("MOUNTEBANK_HOST", "localhost")

class Test_Send(TestCase):
    host = "http://" + MOUNTEBANK + ":8080"

    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)

    def build_request(self):
        payload = dict()
        payload["validation_hash"] = "hash"
        payload["dns_record"] = "self.dns_record"
        payload["public_ip"] = "external_ip"
        return payload

    def test_is_ipv4_valid(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = self.build_request()
        print(updater._send_update(payload))

    def test_is_ipv4_empty(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = dict()
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_none(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = None
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_hash(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = self.build_request()
        del payload["validation_hash"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_record(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = self.build_request()
        del payload["dns_record"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_ip(self):
        updater = UpdateNotifier(dns_record="my.record.tld.", host=self.host, shared_secret="secret")
        payload = self.build_request()
        del payload["public_ip"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))