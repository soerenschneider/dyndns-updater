import configargparse
import logging

from prometheus_client import start_http_server
from inspect import getmembers, isfunction

import ipv4_providers
from dyndns_updater import DyndnsUpdater

def read_config():
    """ Argparse stuff happens here. """
    parser = configargparse.ArgumentParser(prog='dns_client')

    parser.add_argument('-u', '--url', dest="url", action="store", env_var="DNSCLIENT_URL", required=True)
    parser.add_argument('-r', '--record', dest="record", action="store", env_var="DNSCLIENT_RECORD", required=True)
    parser.add_argument('-s', '--secret', dest="shared_secret", action="store", env_var="DNSCLIENT_SECRET", required=True)
    parser.add_argument('--debug', dest="debug", action="store_true", env_var="DNSCLIENT_DEBUG", default=False)
    parser.add_argument('--prometheus_port', dest='promport', action="store", env_var="DNSCLIENT_PROMPORT", type=int, default=8000)
    parser.add_argument('-i', '--interval', dest="interval", action="store", type=int, env_var="DNSCLIENT_INTERVAL", default=1)

    return parser.parse_args()


def get_ipv4_providers():
    return [f for f in getmembers(ipv4_providers, isfunction)]


def init_logging(debug=False):
    loglevel = logging.INFO
    if debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=loglevel)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def print_config(args, ipv4_providers):
    logging.info("Started using the following parameters")
    logging.info("url=%s", args.url)
    logging.info("record=%s", args.record)
    logging.info("interval=%d", args.interval)
    logging.info("prometheus_port=%d", args.promport)
    logging.info("providers=%s", [x[0] for x in ipv4_providers])


def initialize():
    args = read_config()
    init_logging(args.debug)
    ip_providers = get_ipv4_providers()
    start_http_server(args.promport)
    DyndnsUpdater(args.record, args.url, args.shared_secret, ip_providers, args.interval).start()


if __name__ == "__main__":
    initialize()
