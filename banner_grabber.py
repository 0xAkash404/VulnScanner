import socket

# Ports that send a banner immediately on connection (no request needed)
AUTO_BANNER_PORTS = {21, 22, 23, 25, 110, 143, 3306, 5432, 6379, 27017, 11211}

# Ports that speak HTTP and need an HTTP request
HTTP_PORTS = {80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 9090}

# Protocol-specific probes for services that need a specific trigger
PROBES = {
    "http": b"GET / HTTP/1.1\r\nHost: target\r\nConnection: close\r\n\r\n",
    "ftp": None,       # FTP sends banner on connect
    "ssh": None,       # SSH sends banner on connect
    "smtp": None,      # SMTP sends banner on connect
}


def grab_banner(ip, port, timeout=3):
    """Grab a service banner using protocol-appropriate methods."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        # Strategy 1: For auto-banner ports, just receive (the service talks first)
        if port in AUTO_BANNER_PORTS:
            banner = sock.recv(1024)
            sock.close()
            return banner

        # Strategy 2: For HTTP ports, send an HTTP request
        if port in HTTP_PORTS:
            request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            banner = sock.recv(4096)
            sock.close()
            return banner

        # Strategy 3: For unknown ports, first try to receive (maybe it talks first)
        try:
            sock.settimeout(1.5)
            banner = sock.recv(1024)
            if banner:
                sock.close()
                return banner
        except socket.timeout:
            pass

        # If nothing received, try sending an HTTP probe as fallback
        try:
            sock.settimeout(2)
            request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            banner = sock.recv(4096)
            sock.close()
            return banner
        except Exception:
            pass

        sock.close()
        return None

    except Exception:
        return None
