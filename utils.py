import socket
import re
import datetime

def is_valid_ip(target):
    try:
        socket.inet_aton(target)
        return True
    except socket.error:
        return False

def resolve_target(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clean_banner(banner):
    if not banner:
        return "Unknown"
    banner = banner.decode(errors="ignore").strip()
    return re.sub(r'[\r\n]+', ' ', banner)

def calculate_risk_score(vulnerabilities):
    """Calculate overall risk score using CVSS when available, otherwise use severity."""
    score = 0
    for vuln in vulnerabilities:
        # Prefer CVSS score if available
        if "cvss_score" in vuln and vuln["cvss_score"]:
            score += vuln["cvss_score"]
        else:
            # Fallback to severity mapping
            if vuln.get("severity") == "Critical":
                score += 9.8
            elif vuln.get("severity") == "High":
                score += 7.5
            elif vuln.get("severity") == "Medium":
                score += 5.3
            elif vuln.get("severity") == "Low":
                score += 3.9
    return round(score, 1)


def format_eta(remaining_ports, ports_per_sec=None):
    """Format ETA in human-readable format.

    Args:
        remaining_ports: Number of ports left to scan or total ports
        ports_per_sec: Scanning speed in ports/second (optional)

    Returns:
        Human-readable ETA string (e.g., "45m 30s", "2h 15m")
    """
    if ports_per_sec is None:
        ports_per_sec = 100  # Default estimate

    if ports_per_sec <= 0:
        return "unknown"

    seconds = remaining_ports / ports_per_sec

    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)}m {int(seconds % 60)}s"
    else:
        hours = seconds / 3600
        mins = (seconds % 3600) / 60
        return f"{int(hours)}h {int(mins)}m"
