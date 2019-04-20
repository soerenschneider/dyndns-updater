import requests


def ipify_org():
    resp = requests.get('https://api.ipify.org')
    return resp.text, resp.status_code


def ident_me():
    resp = requests.get('https://v4.ident.me/')
    return resp.text, resp.status_code


def seeip_org():
    resp = requests.get('https://ip4.seeip.org/')
    return resp.text, resp.status_code


def whatismyipaddress_com():
    resp = requests.get('http://ipv4bot.whatismyipaddress.com/')
    return resp.text, resp.status_code


def ip_sb():
    resp = requests.get('https://api-ipv4.ip.sb/ip')
    return resp.text, resp.status_code