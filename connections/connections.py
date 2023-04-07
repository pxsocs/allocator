import urllib
import requests
import logging
from time import time
import socket
from datetime import datetime
from backend.utils import pickle_it
import concurrent.futures
from concurrent.futures import wait, ALL_COMPLETED


def url_request(url, method="get", headers=None):
    if not 'http' in url:
        url = 'http://' + url

    try:
        if method == "get":
            request = requests.get(url, timeout=20)
        if method == "post":
            request = requests.post(url, timeout=20)
        return (request)

    except requests.exceptions.ConnectionError:
        return "ConnectionError"

    except Exception:
        return "ConnectionError"

    return request


def url_reachable(url):
    request = url_request(url)
    try:
        if request == 'ConnectionError':
            return False
        else:
            return True
    except Exception:
        return True


def url_parser(url):
    # Parse it
    from urllib.parse import urlparse
    parse_object = urlparse(url)
    scheme = 'http' if parse_object.scheme == '' else parse_object.scheme
    if parse_object.netloc != '':
        url = scheme + '://' + parse_object.netloc + '/'
    if not url.startswith('http'):
        url = 'http://' + url
    if url[-1] != '/':
        url += '/'

    return (url)


def get_local_ip():
    from backend.utils import pickle_it
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    pickle_it('save', 'local_ip_address.pkl', local_ip_address)
    return (local_ip_address)


def get_local_host_name():
    return (socket.gethostname())


#  Check if a port at localhost is in use
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0



# Checks for internet connection
# Saved to: internet_connected.pkl
# Returns: True / False
def internet_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    connected = False
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        connected = True
    except socket.error:
        connected = False
    pickle_it('save', 'diags_internet_connected.pkl', connected)
    return (connected)


