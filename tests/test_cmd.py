import argparse
import logging

from unittest import TestCase
from dns_client import get_ipv4_providers, print_config

class TestCmd(TestCase):
    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def test_print_config(self):
        args = argparse.Namespace(url="http://host.tld", record="bla.blub.bla.", interval=60, promport=8181)
        providers = get_ipv4_providers()
        print_config(args, providers)
        