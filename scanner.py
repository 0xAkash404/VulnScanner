import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from banner_grabber import grab_banner
from service_detector import detect_service
from cve_checker import check_vulnerabilities
from utils import clean_banner, calculate_risk_score, resolve_target, format_eta


def scan_port(ip, port):
    """Scan a single port and return result dict if open, else None."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            banner = grab_banner(ip, port)
            service, version = detect_service(port, banner)
            vulnerabilities = check_vulnerabilities(service, version)

            return {
                "port": port,
                "service": service,
                "version": version if version != "Unknown" else (clean_banner(banner) if banner else "Unknown"),
                "banner_raw": clean_banner(banner) if banner else "",
                "vulnerabilities": vulnerabilities,
                "risk_score": calculate_risk_score(vulnerabilities),
                "vuln_count": len(vulnerabilities),
            }
    except Exception as e:
        pass

    return None


def start_scan(target, port_range=(1, 65535), timeout=1.5, max_workers=100, callback=None):
    """Scan a target across a port range using a bounded thread pool.

    Args:
        target: Hostname or IP to scan
        port_range: Tuple of (start_port, end_port) to scan
        timeout: Socket timeout in seconds
        max_workers: Maximum concurrent threads
        callback: Optional callback function for progress updates

    Returns:
        Tuple (results_list, scan_stats_dict)
    """
    # Resolve hostname to IP
    ip = resolve_target(target)
    if ip is None:
        print(f"[Scanner] Could not resolve target: {target}")
        return [], {
            "total_ports": 0,
            "open_ports": 0,
            "scan_time": 0,
            "ports_per_second": 0,
            "status": "failed"
        }

    port_count = port_range[1] - port_range[0]
    print(f"[Scanner] Scanning {target} ({ip}), ports {port_range[0]}-{port_range[1] - 1} ({port_count} ports)")
    print(f"[Scanner] Using {max_workers} concurrent threads, timeout {timeout}s")
    print(f"[Scanner] Estimated time: {format_eta(port_count, max_workers)}")
    print()

    results = []
    actual_workers = min(max_workers, port_count)
    start_time = time.time()
    ports_scanned = 0

    # Lock for thread-safe updates
    scan_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=actual_workers) as executor:
        futures = {
            executor.submit(scan_port, ip, port): port
            for port in range(port_range[0], port_range[1])
        }

        for i, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                if result is not None:
                    with scan_lock:
                        results.append(result)

                ports_scanned = i
                elapsed = time.time() - start_time

                # Update progress every 100 ports or use callback
                if i % 100 == 0:
                    ports_per_sec = ports_scanned / elapsed if elapsed > 0 else 0
                    remaining = port_count - ports_scanned
                    eta_secs = remaining / ports_per_sec if ports_per_sec > 0 else 0

                    progress_pct = (i / port_count) * 100
                    print(f"[Scanner] [{progress_pct:5.1f}%] Scanned {i}/{port_count} ports | "
                          f"Found {len(results)} open | ETA: {format_eta(remaining, ports_per_sec)}")

                    if callback:
                        callback({
                            "progress": progress_pct,
                            "scanned": i,
                            "total": port_count,
                            "open": len(results),
                            "eta": eta_secs,
                            "elapsed": elapsed
                        })
            except Exception as e:
                pass

    # Sort by port number
    results.sort(key=lambda r: r["port"])

    total_time = time.time() - start_time
    total_vulns = sum(r["vuln_count"] for r in results)
    critical_count = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "Critical")
    high_count = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "High")

    stats = {
        "total_ports": port_count,
        "open_ports": len(results),
        "total_vulnerabilities": total_vulns,
        "critical": critical_count,
        "high": high_count,
        "scan_time": total_time,
        "ports_per_second": port_count / total_time if total_time > 0 else 0,
        "status": "completed"
    }

    print()
    print(f"[Scanner] ✓ Scan complete in {total_time:.1f}s")
    print(f"[Scanner] Results: {len(results)} open ports, {total_vulns} vulnerabilities")
    print(f"[Scanner]  - Critical: {critical_count} | High: {high_count}")
    print(f"[Scanner]  - Speed: {stats['ports_per_second']:.0f} ports/sec")

    return results, stats
