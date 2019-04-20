import requests
import random
import hashlib
import logging
import json
import time

from prometheus_client import Counter, Gauge


class DyndnsUpdater:
    prom_backends_status = Counter('dnsclient_backends_http_status', 'HTTP code of backend calls', ['site', 'status'])
    prom_backends_fetching_ip_failed = Counter('dnsclient_backends_fetching_ip_failed', 'Fetching IP failed')
    prom_last_check = Gauge('dnsclient_update_last_check_timestamp_seconds', 'Timestamp of the latest check for a new IP')
    prom_update_detected = Counter('dnsclient_update_detected_total', 'Amount of IP updates detected')
    prom_update_detected_ts = Gauge('dnsclient_update_detected_timestamp_seconds', 'Timestamp of update')
    prom_update_request_status_code = Counter('dnsclient_request_status_code', 'Status code of request', ['status_code'])

    def __init__(self, dns_record, host, shared_secret, ip_providers, interval=1):
        self.dns_record = dns_record
        self.host = host
        self.shared_secret = shared_secret
        self.ip_providers = ip_providers
        self.interval = interval

        if not ip_providers:
            raise ValueError("No providers for determing IP address found. ")

    @staticmethod
    def shuffle_providers(self, providers):
        """ Makes sure we're using the providers more or less evenly. """
        random.shuffle(providers)

    @staticmethod
    def hash_request(host, external_ip, shared_secret):
        """ 'Sign' our request with the shared secret. """
        return hashlib.sha256(f"{host}{external_ip}{shared_secret}".encode('utf-8')).hexdigest()

    def update(self, external_ip):
        """ Notify the server about an updated IP address. """
        payload = dict()
        payload["validation_hash"] = self.hash_request(self.dns_record, external_ip, self.shared_secret)
        payload["dns_record"] = self.dns_record
        payload["public_ip"] = external_ip

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(self.host, data=json.dumps(payload), headers=headers)
        self.prom_update_request_status_code.labels(response.status_code).inc()
        logging.debug(f"Response from remote: {response.status_code}")

    def get_external_ip(self, backends):
        """ Iterate all IP providers until the first one gives a valid response.  """
        self.prom_last_check.set(int(time.time()))
        for provider in self.ip_providers:
            try:
                external_ip, status_code = provider[1]()
                self.prom_backends_status.labels(provider[0], status_code).inc()
                external_ip = external_ip.strip()

                # before proceeding make sure this provider didn't provide garbage
                # todo: validate ipv4 and ipv6
                if external_ip and status_code / 100 == 2:
                    return external_ip

            except Exception:
                logging.debug(f"Failed to fetch information from provider {provider[0]}")

        self.prom_backends_fetching_ip_failed.inc()
        logging.error("Giving up after all providers failed: Is the network down?")

    def has_update_occured(self, last_ip, fetched_ip):
        """ Returns True when a IP change has been detected, otherwise False. """
        if fetched_ip is not None and last_ip != fetched_ip:
            logging.info(f"Detected new IP -> {fetched_ip}")
            self.prom_update_detected.inc()
            now = int(time.time())
            self.prom_update_detected_ts.set(now)
            return True

        logging.debug("No update detected")
        return False

    def start(self):
        last_ip = None
        while True:
            try:
                self.shuffle_providers(self.ip_providers)
                fetched_ip = self.get_external_ip(self.ip_providers)

                if self.has_update_occured(last_ip, fetched_ip) is True:
                    last_ip = fetched_ip
                    self.update(fetched_ip)

                time.sleep(60 * self.interval)
            except KeyboardInterrupt:
                return
            except Exception as e:
                time.sleep(60 * self.interval)
                logging.error(f"Error while updating: {e}")