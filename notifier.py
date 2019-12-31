import hashlib
import json
import logging

import backoff
import requests
from prometheus_client import Counter


prom_update_request_status_code = Counter('dnsclient_update_requests_total', 'Status code of request', ['status_code'])


class UpdateNotifier:
    def __init__(self, dns_record, host, shared_secret):
        self._set_dns_record(dns_record)

        if not host:
            raise ValueError("host not specified")
        self.host = host

        if not shared_secret:
            raise ValueError("secret not specified")
        self.shared_secret = shared_secret

    def _set_dns_record(self, dns_record):
        """
        Set the DNS record. The model requires the record to end with a dot,
        so make sure here it is set.
        """
        if not dns_record:
            raise ValueError("dns_record not specified")

        if not dns_record.endswith("."):
            dns_record += "."
        self.dns_record = dns_record

    def notify_update(self, fetched_ip):
        payload = self._build_request(fetched_ip)
        self._send_update(payload)
    
    @staticmethod
    def hash_request(host, external_ip, shared_secret):
        """ 'Sign' our request with the shared secret. """
        if not host or not external_ip or not shared_secret:
            raise ValueError("Uninitialized value provided")

        return hashlib.sha256(f"{host}{external_ip}{shared_secret}".encode('utf-8')).hexdigest()

    def _build_request(self, external_ip):
        """ Create request object to send to the endpoint. """

        if not external_ip:
            raise ValueError("Can not build request object, external_ip is missing")
        
        payload = dict()
        payload["validation_hash"] = UpdateNotifier.hash_request(self.dns_record, external_ip, self.shared_secret)
        payload["dns_record"] = self.dns_record
        payload["public_ip"] = external_ip
        return payload

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10)
    def _send_update(self, payload):
        """ Notify the server about an updated IP address. """
        if not payload:
            raise ValueError("payload must not be empty")

        logging.info("Sending update to remote server")

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(self.host, data=json.dumps(payload), headers=headers)
        
        prom_update_request_status_code.labels(response.status_code).inc()
        logging.debug("Response from remote: %s", response.status_code)
        if response.status_code >= 400:
            raise ValueError()