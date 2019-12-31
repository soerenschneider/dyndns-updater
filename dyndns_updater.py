import random
import logging
import ipaddress
import time

import backoff
import requests
from prometheus_client import Counter, Gauge
from persistence import Persistence

prom_ipresolver_status = Counter('dnsclient_ipresolver_count_total', 'Amount of calls for external IP resolving', ['site', 'status_code'])
prom_ipresolver_failed = Counter('dnsclient_ipresolver_failed_total', 'Amount of failed external IP discoverings')
prom_last_check = Gauge('dnsclient_last_check_ts_seconds', 'Timestamp of the latest check for a new IP')
prom_update_detected = Counter('dnsclient_updates_detected_total', 'Amount of IP updates detected')
prom_update_detected_ts = Gauge('dnsclient_last_detected_update_ts_seconds', 'Timestamp of update')
prom_backend_errors = Counter('dnsclient_backend_errors_total', 'Errors with backend interaction', ['operation', 'backend_name'])


class UpdateDetector:
    def __init__(self, update_notifier, ip_providers, interval=None, persistence=None):
        if not update_notifier:
            raise ValueError("No update_notifier configured")
        self.update_notifier = update_notifier

        if not ip_providers:
            raise ValueError("No providers for determing IP address found")
        self.ip_providers = ip_providers
        
        if not interval:
            interval = 60
        self.interval = interval

        if not persistence:
            persistence = Persistence()
        self.persistence_backend = persistence

        self._quit = False
    
    @staticmethod
    def shuffle_providers(providers):
        """ Makes sure we're using the providers more or less evenly. """
        if providers:
            random.shuffle(providers)

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
                external_ip, status_code = UpdateDetector.request_wrapper(provider[1])
                prom_ipresolver_status.labels(provider[0], status_code).inc()
                if external_ip:
                    external_ip = external_ip.strip()
                    # before proceeding make sure this provider didn't provide garbage
                    if UpdateDetector.is_valid_ipv4(external_ip) is True and status_code < 400:
                        return external_ip
            except Exception as err:
                logging.debug("Failed to fetch information from provider '%s': %s", provider[0], err)

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
            self.update_notifier.notify_update(fetched_ip)
            self._write_to_persistence_backend(fetched_ip)
            
        return fetched_ip

    def _write_to_persistence_backend(self, new_ip: str) -> None:
        logging.debug("Writing IP to persistence backend '%s'", self.persistence_backend.get_plugin_name())
        try:
            self.persistence_backend.write(new_ip)
        except Exception as err:
            prom_backend_errors.labels("write", self.persistence_backend.get_plugin_name()).inc()
            logging.error("Could not write IP to persistence backend '%s': %s", self.persistence_backend.get_plugin_name(), err)

    def _read_from_persistence_backend(self) -> str:
        try:
            return self.persistence_backend.read()
        except Exception as err:
            prom_backend_errors.labels("read", self.persistence_backend.get_plugin_name()).inc()
            logging.warning("Could not read old IP from persistence backend '%s': %s", self.persistence_backend.get_plugin_name(), err)
            return None

    def quit(self):
        self._quit = True

    def start(self):
        logging.info("Started!")

        last_ip = self._read_from_persistence_backend()
        logging.info("Read %s from persistence backend", last_ip)

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