from unittest import TestCase
from inspect import getmembers, isfunction

import logging
import ipv4_providers

class TestProviders(TestCase):
    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)

    def test_providers(self):
        providers = [f for f in getmembers(ipv4_providers, isfunction)]
        logging.info("Got %d providers", len(providers))
        failing_providers = list()
        for provider in providers:
            ip, code = provider[1]()
            if ip:
                ip = ip.strip()
            if not ip or code >= 400:
                failing_providers.append(provider[0])

        if len(failing_providers) > 0:
            msg = "The following providers failed: {}".format(failing_providers)
            logging.info(msg)
            self.fail(msg)
