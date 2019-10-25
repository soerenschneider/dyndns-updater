from dyndns_updater import DyndnsUpdater
from unittest import TestCase

class TestRequests(TestCase):

    def test_build_request(self):
        dns_record = "my.dns.tld."
        host = "remote.host" 
        shared_secret = "secret" 
        ip_providers = [""]
        d = DyndnsUpdater(dns_record, host, shared_secret, ip_providers)
        req = d._build_request("1.2.3.4")
        assert req is not None
        assert req['dns_record'] == dns_record
        assert req['public_ip'] == '1.2.3.4'
        assert len(req['validation_hash']) > 1


    def test_build_request_emtpy(self):
        dns_record = "my.dns.tld."
        host = "remote.host" 
        shared_secret = "secret" 
        ip_providers = [""]
        d = DyndnsUpdater(dns_record, host, shared_secret, ip_providers)
        with self.assertRaises(ValueError):
            d._build_request("")

    def test_build_request_none(self):
        dns_record = "my.dns.tld."
        host = "remote.host" 
        shared_secret = "secret" 
        ip_providers = [""]
        d = DyndnsUpdater(dns_record, host, shared_secret, ip_providers)
        with self.assertRaises(ValueError):
            d._build_request(None)

