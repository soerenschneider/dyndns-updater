from dyndns_updater import DyndnsUpdater
import pytest

def test_build_request():
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


def test_build_request_emtpy():
    dns_record = "my.dns.tld."
    host = "remote.host" 
    shared_secret = "secret" 
    ip_providers = [""]
    d = DyndnsUpdater(dns_record, host, shared_secret, ip_providers)
    with pytest.raises(ValueError):
        d._build_request("")

def test_build_request_none():
    dns_record = "my.dns.tld."
    host = "remote.host" 
    shared_secret = "secret" 
    ip_providers = [""]
    d = DyndnsUpdater(dns_record, host, shared_secret, ip_providers)
    with pytest.raises(ValueError):
        d._build_request(None)

