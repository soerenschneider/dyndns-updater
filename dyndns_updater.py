import random
import hashlib
import logging
import json
import ipaddress
import time

import backoff
import requests
from prometheus_client import Counter, Gauge

prom_ipresolver_status = Counter('dnsclient_ipresolver_count_total', 'Amount of calls for external IP resolving', ['site', 'status_code'])
prom_ipresolver_failed = Counter('dnsclient_ipresolver_failed_total', 'Amount of failed external IP discoverings')
prom_last_check = Gauge('dnsclient_last_check_ts_seconds', 'Timestamp of the latest check for a new IP')
prom_update_detected = Counter('dnsclient_updates_detected_total', 'Amount of IP updates detected')
prom_update_detected_ts = Gauge('dnsclient_last_detected_update_ts_seconds', 'Timestamp of update')
prom_update_request_status_code = Counter('dnsclient_update_requests_total', 'Status code of request', ['status_code'])

class DyndnsUpdater:
    def __init__(self, dns_record, host, shared_secret, ip_providers, interval=None):
        self._set_dns_record(dns_record)

        if not host:
            raise ValueError("host not specified")
        self.host = host

        if not shared_secret:
            raise ValueError("secret not specified")
        self.shared_secret = shared_secret
        
        if not ip_providers:
            raise ValueError("No providers for determing IP address found. ")
        self.ip_providers = ip_providers
        
        if not interval:
            interval = 60
        self.interval = interval

        self._quit = False

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


    @staticmethod
    def shuffle_providers(providers):
        """ Makes sure we're using the providers more or less evenly. """
        if providers:
            random.shuffle(providers)

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
        payload["validation_hash"] = DyndnsUpdater.hash_request(self.dns_record, external_ip, self.shared_secret)
        payload["dns_record"] = self.dns_record
        payload["public_ip"] = external_ip
        return payload

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
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

    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """ Check whether the supplied argument is a valid IPv4 address """
        if not ip:
            return False

        try:
            parsed = ipaddress.ip_interface(ip)
            return isinstance(parsed, ipaddress.IPv4Interface)
        except ValueError:
            return False

    @staticmethod
    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
    def request_wrapper(provider_function):
        """
        Wrapper using a backoff annotation that just executes the function to fetch data
        from IP provider.
        """
        if not provider_function:
            raise ValueError("No function to call provided")

        return provider_function()

    def get_external_ip(self):
        """ Iterate all IP providers until the first one gives a valid response. """
        prom_last_check.set_to_current_time()
        
        for provider in self.ip_providers:
            try:
                external_ip, status_code = DyndnsUpdater.request_wrapper(provider[1])
                prom_ipresolver_status.labels(provider[0], status_code).inc()
                if not external_ip:
                    return None

                external_ip = external_ip.strip()

                # before proceeding make sure this provider didn't provide garbage
                if DyndnsUpdater.is_valid_ipv4(external_ip) is True and status_code < 400:
                    return external_ip

            except Exception:
                logging.debug("Failed to fetch information from provider '%s'", provider[0])

        prom_ipresolver_failed.inc()
        logging.error("Giving up after all providers failed: Is the network down?")
        return None

    @staticmethod
    def has_update_occured(last_ip, fetched_ip):
        """ Returns True when a IP change has been detected, otherwise False. """
        if fetched_ip and last_ip != fetched_ip:
            logging.info("Detected new IP -> %s", fetched_ip)
            prom_update_detected.inc()
            prom_update_detected_ts.set_to_current_time()
            return True

        logging.debug("No update detected")
        return False

    def perform_check(self, last_ip):
        self.shuffle_providers(self.ip_providers)
        fetched_ip = self.get_external_ip()

        if self.has_update_occured(last_ip, fetched_ip) is True:
            payload = self._build_request(fetched_ip)
            self._send_update(payload)
            
        return fetched_ip

    def quit(self):
        self._quit = True

    def start(self):
        logging.info("Started!")
        last_ip = None
        while not self._quit:
            try:
                last_ip = self.perform_check(last_ip)
                time.sleep(self.interval)
            except KeyboardInterrupt:
                logging.info("Received signal, quitting")
                self.quit()
            except Exception as error:
                time.sleep(self.interval)
                logging.error("Error while updating: %s", error)
