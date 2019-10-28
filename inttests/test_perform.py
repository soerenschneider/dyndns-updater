import os
import logging

from unittest import TestCase
from dyndns_updater import DyndnsUpdater

MOUNTEBANK = os.getenv("MOUNTEBANK_HOST", "localhost")

ip = "1.1.1.1"
def resolve_ip():
    return "1.1.1.1", 200

class Test_Send(TestCase):
    host = "http://" + MOUNTEBANK + ":8080"

    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)

    def test_is_ipv4_valid(self):
        updater = DyndnsUpdater(dns_record="my.record.tld.", host=self.host, shared_secret="secret", ip_providers=[("resolve_ip", resolve_ip)])
        resolved_ip = updater.perform("1.1.1.0")
        self.assertEqual(ip, resolved_ip)
