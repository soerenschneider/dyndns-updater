import logging
from inspect import getmembers, isfunction

import configargparse
import ipv4_providers

from prometheus_client import start_http_server
from dyndns_updater import DyndnsUpdater

from persistence import FilePersistence


def read_config():
    """ Parse CLI args. """
    parser = configargparse.ArgumentParser(prog='dns_client')

    parser.add_argument('-u', '--url', dest="url", action="store", env_var="DNSCLIENT_URL", required=True, help="The URL of the server component")
    parser.add_argument('-r', '--record', dest="record", action="store", env_var="DNSCLIENT_RECORD", required=True, help="The full DNS record to update. It should end with a dot")
    parser.add_argument('-s', '--secret', dest="shared_secret", action="store", env_var="DNSCLIENT_SECRET", required=True, help="The secret that's associated with the appropriate record")
    parser.add_argument('--debug', dest="debug", action="store_true", env_var="DNSCLIENT_DEBUG", default=False, help="Print debug messages")
    parser.add_argument('--prometheus_port', dest='promport', action="store", env_var="DNSCLIENT_PROMPORT", type=int, default=0, help="Start a prometheus metrics server on the given port. To disable this feature, supply 0 as port. (Defaults to 0)")
    parser.add_argument('-i', '--interval', dest="interval", action="store", type=int, env_var="DNSCLIENT_INTERVAL", default=60, help="The interval in seconds to check a random IP provider. Defaults to 60")
    parser.add_argument('-f', '--file', dest="file", action="store", env_var="DNSCLIENT_FILE", required=False, help="Save resolved IP to a file to preserve the status across service restarts.")

    return parser.parse_args()


def get_ipv4_providers():
    """ Return all configured IP providers """
    logging.info("Loading IP providers")
    return [f for f in getmembers(ipv4_providers, isfunction)]


def init_logging(debug=False):
    """ Setup logging """
    loglevel = logging.INFO
    if debug:
        loglevel = logging.DEBUG
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=loglevel)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def print_config(args, ipv4_providers):
    """ Print configuration after startup """
    logging.info("Using the following parameters")
    logging.info("url=%s", args.url)
    logging.info("record=%s", args.record)
    logging.info("interval=%d", args.interval)
    logging.info("prometheus_port=%d", args.promport)
    if "file" in args:
        logging.info("file=%s", args.file)
    logging.info("providers=%s", [x[0] for x in ipv4_providers])


def prometheus_server(args):
    if args.promport < 1:
        logging.info("Not starting prometheus metrics endpoint")
        return

    logging.info("Start prometheus metrics endpoint at %d", args.promport)
    start_http_server(args.promport)


def initialize():
    """ Start up """
    args = read_config()

    persistence_provider = None
    if args.file:
        persistence_provider = FilePersistence(args.file)

    init_logging(args.debug)
    ip_providers = get_ipv4_providers()
    print_config(args, ip_providers)
    prometheus_server(args)
    updater = DyndnsUpdater(
        dns_record=args.record, 
        host=args.url, 
        shared_secret=args.shared_secret, 
        ip_providers=ip_providers, 
        interval=args.interval, 
        persistence=persistence_provider)
    updater.start()


if __name__ == "__main__":
    initialize()
