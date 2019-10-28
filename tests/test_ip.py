from unittest import TestCase

from dyndns_updater import DyndnsUpdater

class TestIp(TestCase):
    def test_is_ipv4_valid(self):
        response = DyndnsUpdater.is_valid_ipv4("192.168.0.1")
        self.assertTrue(response)
    
    def test_is_ipv4_valid_2(self):
        response = DyndnsUpdater.is_valid_ipv4("8.8.8.8")
        self.assertTrue(response)

    def test_is_ipv4_invalid_ipv6(self):
        response = DyndnsUpdater.is_valid_ipv4("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        self.assertFalse(response)

    def test_is_ipv4_invalid_empty(self):
        response = DyndnsUpdater.is_valid_ipv4("")
        self.assertFalse(response)

    def test_is_ipv4_invalid_none(self):
        response = DyndnsUpdater.is_valid_ipv4(None)
        self.assertFalse(response)

    def test_is_ipv4_invalid_almost_ipv4(self):
        response = DyndnsUpdater.is_valid_ipv4("192.168.0")
        self.assertFalse(response)