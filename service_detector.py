import re

# Extended port-to-service mapping
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 67: "DHCP",
    80: "HTTP", 110: "POP3", 111: "RPCBind", 119: "NNTP", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP-Trap", 389: "LDAP",
    443: "HTTPS", 445: "SMB", 465: "SMTPS", 587: "SMTP", 636: "LDAPS",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle", 2049: "NFS",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "HTTP-Alt",
    9090: "HTTP-Alt", 9200: "Elasticsearch", 9300: "Elasticsearch-Node",
    11211: "Memcached", 27017: "MongoDB", 27018: "MongoDB", 50000: "SAP",
    3128: "Squid-Proxy", 5060: "SIP", 5061: "SIPS", 1194: "OpenVPN",
    10000: "Webmin", 10001: "Swat", 512: "Rsh", 513: "Rlogin", 514: "Syslog",
}

# Patterns to detect services from banner content (enhanced)
BANNER_PATTERNS = [
    (r"Apache[/ ]+(\d+\.\d+\.\d+\S*)", "Apache HTTP"),
    (r"nginx[/ ]+(\d+\.\d+\.\d+\S*)", "Nginx"),
    (r"OpenSSH[_ ]+(\d+\.\d+\S*)", "OpenSSH"),
    (r"Microsoft-IIS[/ ]+(\d+\.\d+\S*)", "Microsoft IIS"),
    (r"LiteSpeed[/ ]+(\d+\.\d+\S*)", "LiteSpeed"),
    (r"vsftpd\s+(\d+\.\d+\.\d+\S*)", "vsftpd"),
    (r"ProFTPD\s+(\d+\.\d+\.\d+\S*)", "ProFTPD"),
    (r"Pure-FTPd", "Pure-FTPd"),
    (r"FileZilla Server\s+(\d+\.\d+\S*)", "FileZilla FTP"),
    (r"Postfix", "Postfix SMTP"),
    (r"Exim\s+(\d+\.\d+\S*)", "Exim SMTP"),
    (r"Sendmail[/ ]+(\d+\.\d+\S*)", "Sendmail"),
    (r"Dovecot", "Dovecot"),
    (r"MySQL[/ ]+(\d+\.\d+\.\d+\S*)", "MySQL"),
    (r"MariaDB[- ]+(\d+\.\d+\.\d+\S*)", "MariaDB"),
    (r"PostgreSQL[/ ]+(\d+\.\d+\S*)", "PostgreSQL"),
    (r"Redis[/ ]+server\s+v=(\d+\.\d+\.\d+\S*)", "Redis"),
    (r"redis_version:(\d+\.\d+\.\d+\S*)", "Redis"),
    (r"MongoDB", "MongoDB"),
    (r"Microsoft-HTTPAPI[/ ]+(\d+\.\d+)", "Microsoft HTTPAPI"),
    (r"Tomcat[/ ]+(\d+\.\d+\.\d+\S*)", "Apache Tomcat"),
    (r"Jetty[/ ]+(\d+\.\d+\.\d+\S*)", "Jetty"),
    (r"PHP[/ ]+(\d+\.\d+\.\d+\S*)", "PHP"),
    (r"Server:\s*cloudflare", "Cloudflare"),
    (r"X-Powered-By:\s*Express", "Node.js Express"),
    (r"X-Powered-By:\s*ASP\.NET", "ASP.NET"),
    (r"Dropbear\s+sshd\s+(\d+\.\d+\S*)", "Dropbear SSH"),
    (r"OpenSSL[/ ]+(\d+\.\d+\.\d+\S*)", "OpenSSL"),
    (r"mod_ssl[/ ]+(\d+\.\d+\.\d+\S*)", "mod_ssl"),
    (r"WildFly[/ ]+(\d+\.\d+\S*)", "WildFly"),
    (r"GlassFish[/ ]+(\d+\.\d+\S*)", "GlassFish"),
    (r"JBoss[/ ]+(\d+\.\d+\S*)", "JBoss"),
    (r"Elasticsearch[/ ]+(\d+\.\d+\.\d+\S*)", "Elasticsearch"),
    (r"Kibana[/ ]+(\d+\.\d+\.\d+\S*)", "Kibana"),
    (r"Jenkins[/ ]+(\d+\.\d+\S*)", "Jenkins"),
    (r"Splunk[/ ]+(\d+\.\d+\S*)", "Splunk"),
    (r"SonicWall", "SonicWall Firewall"),
    (r"Palo Alto", "Palo Alto Firewall"),
    (r"Cisco", "Cisco Device"),
    (r"Fortinet", "Fortinet Device"),
]

# Regex to extract version-like strings from banners
VERSION_REGEX = re.compile(r'(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9._-]*))')


def detect_service(port, banner):
    """Detect service name and extract version from port number and banner."""
    service = COMMON_PORTS.get(port, "Unknown")
    version = "Unknown"

    if not banner:
        return service, version

    banner_str = banner.decode(errors="ignore").strip()

    if not banner_str:
        return service, version

    # Try each banner pattern to identify the service and version
    for pattern, svc_name in BANNER_PATTERNS:
        match = re.search(pattern, banner_str, re.IGNORECASE)
        if match:
            service = svc_name
            # Extract version from capture group if present
            if match.lastindex and match.lastindex >= 1:
                version = match.group(1)
            else:
                # Try to find a version number near the service name
                ver_match = VERSION_REGEX.search(banner_str)
                if ver_match:
                    version = ver_match.group(1)
            break

    # If no pattern matched but we have a banner, try to extract any version
    if version == "Unknown" and banner_str:
        ver_match = VERSION_REGEX.search(banner_str)
        if ver_match:
            version = ver_match.group(1)

    return service, version
