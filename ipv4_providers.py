import requests

TIMEOUT_SECONDS=5

def ipify_org():
    """ IP Provider for ipify.org """
    resp = requests.get('https://api.ipify.org', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code


def ident_me():
    """ IP Provider for v4.ident.me """
    resp = requests.get('https://v4.ident.me/', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code


def seeip_org():
    """ IP Provider for ipv4.seeip.org """
    resp = requests.get('https://ip4.seeip.org/', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code


def whatismyipaddress_com():
    """ IP Provider for ipv4bot.whatismyipaddress.com """
    resp = requests.get('http://ipv4bot.whatismyipaddress.com/', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code


def ip_sb():
    """ IP Provider for api-ipv4.ip.sb """
    resp = requests.get('https://api-ipv4.ip.sb/ip', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code

def myip_io():
    """ IP Provider for api-ipv4.ip.sb """
    resp = requests.get('https://api4.my-ip.io/ip', timeout=TIMEOUT_SECONDS)
    return resp.text, resp.status_code
