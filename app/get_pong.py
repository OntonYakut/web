import socket
import re

def get_pong(server):
    ip_regexp = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"
    if server:
        if re.match(ip_regexp, server) is not None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((server, 22))
                s.close()
                return True
            except socket.error:
                return False
