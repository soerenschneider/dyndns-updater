from unittest import TestCase
from inspect import getmembers, isfunction

import logging
import ipv4_providers

class TestProviders(TestCase):
    @staticmethod
    def setUpClass():
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def test_providers(self):
        providers = [f for f in getmembers(ipv4_providers, isfunction)]
        logging.info("Got %d providers", len(providers))

        failing_providers = list()
        ips = list()

        for provider in providers:
            logging.debug("Trying provider %s", provider[0])
            ip, code = provider[1]()
            ip = ip.strip()

            logging.debug("Got '%s' with code %s from %s", ip, code, provider[0])
            ips.append(ip)
            if not ip or code >= 400:
                failing_providers.append(provider[0])

        if len(failing_providers) > 0:
            msg = "The following providers failed: {}".format(failing_providers)
            logging.error(msg)
            self.fail(msg)

        if len(set(ips)) != 1:
            msg = "Received different IPs"
            logging.error(msg)
            self.fail(msg)
