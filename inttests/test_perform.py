import os
import logging

from unittest import TestCase
from dyndns_updater import UpdateDetector

MOUNTEBANK = os.getenv("MOUNTEBANK_HOST", "localhost")

ip = "1.1.1.1"
def resolve_ip():
    return "1.1.1.1", 200

class Dummy(object):
    def notify_update(self, ip):
        pass

class Test_Send(TestCase):
    host = "http://" + MOUNTEBANK + ":8080"

    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)

    def test_is_ipv4_valid(self):
        dummy = Dummy()
        updater = UpdateDetector(update_notifier=dummy, ip_providers=[("resolve_ip", resolve_ip)])
        resolved_ip = updater.perform_check("1.1.1.0")
        self.assertEqual(ip, resolved_ip)
