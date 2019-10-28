import os
import logging

from unittest import TestCase
from dyndns_updater import DyndnsUpdater

def resolve_ip():
    return "1.1.1.1"

class Test_Send(TestCase):
    host = os.getenv("DYNDNS_MOUNTEBANK", "http://localhost:8080")

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
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = self.build_request()
        print(updater._send_update(payload))

    def test_is_ipv4_empty(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = dict()
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_none(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = None
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_hash(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = self.build_request()
        del payload["validation_hash"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_record(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = self.build_request()
        del payload["dns_record"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))

    def test_is_ipv4_missing_ip(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[resolve_ip])
        payload = self.build_request()
        del payload["public_ip"]
        with self.assertRaises(ValueError):
            print(updater._send_update(payload))