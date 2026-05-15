"""
Command-line interface for the Vulnerability Scanner.
Allows automated scanning and report generation from CLI.
"""

import argparse
import sys
import json
from pathlib import Path
from scanner import start_scan
from report_generator import generate_pdf_report
from utils import get_timestamp
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_json(results, target):
    """Export scan results as JSON."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    safe_target = "".join(c if c.isalnum() or c in ".-_" else "_" for c in target)
    filename = reports_dir / f"scan_report_{safe_target}.json"

    report = {
        "target": target,
        "scan_date": get_timestamp(),
        "total_ports": len(results),
        "total_vulnerabilities": sum(len(r["vulnerabilities"]) for r in results),
        "critical_count": sum(1 for r in results for v in r["vulnerabilities"]
                            if v.get("severity") == "Critical"),
        "high_count": sum(1 for r in results for v in r["vulnerabilities"]
                         if v.get("severity") == "High"),
        "ports": results
    }

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    return str(filename)


def export_csv(results, target):
    """Export scan results as CSV."""
    import csv

    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    safe_target = "".join(c if c.isalnum() or c in ".-_" else "_" for c in target)
    filename = reports_dir / f"scan_report_{safe_target}.csv"

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Port", "Service", "Version", "CVE ID", "Severity", "CVSS Score",
                        "Vulnerability Type", "Description"])

        for result in results:
            port = result["port"]
            service = result["service"]
            version = result["version"]

            if result["vulnerabilities"]:
                for vuln in result["vulnerabilities"]:
                    writer.writerow([
                        port,
                        service,
                        version,
                        vuln.get("cve_id", "N/A"),
                        vuln.get("severity", "Unknown"),
                        vuln.get("cvss_score", "N/A"),
                        vuln.get("vuln_type", "Unknown"),
                        vuln.get("description", "")[:100]
                    ])
            else:
                writer.writerow([port, service, version, "", "", "", "", "No vulnerabilities"])

    return str(filename)


def export_html(results, target):
    """Export scan results as HTML."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    safe_target = "".join(c if c.isalnum() or c in ".-_" else "_" for c in target)
    filename = reports_dir / f"scan_report_{safe_target}.html"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Vulnerability Scan Report - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin: 15px 0; }}
        th {{ background: #3498db; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
        .high {{ color: #e67e22; font-weight: bold; }}
        .medium {{ color: #f39c12; font-weight: bold; }}
        .low {{ color: #27ae60; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Vulnerability Scan Report</h1>
        <p>Target: <strong>{target}</strong></p>
        <p>Scan Date: {get_timestamp()}</p>
    </div>
"""

    total_vulns = sum(len(r["vulnerabilities"]) for r in results)
    critical = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "Critical")
    high = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "High")

    html += f"""
    <div class="summary">
        <h2>Summary</h2>
        <p>Open Ports: <strong>{len(results)}</strong> | Total Vulnerabilities: <strong>{total_vulns}</strong> |
        Critical: <span class="critical">{critical}</span> | High: <span class="high">{high}</span></p>
    </div>

    <h2>Port/Service Summary</h2>
    <table>
        <tr>
            <th>Port</th>
            <th>Service</th>
            <th>Version</th>
            <th>Vulnerabilities</th>
            <th>Risk Score</th>
        </tr>
"""

    for r in results:
        html += f"""        <tr>
            <td>{r['port']}</td>
            <td>{r['service']}</td>
            <td>{r['version'][:50]}</td>
            <td>{r['vuln_count']}</td>
            <td><strong>{r['risk_score']}</strong></td>
        </tr>
"""

    html += """    </table>

    <h2>Vulnerability Details</h2>
    <table>
        <tr>
            <th>Port</th>
            <th>Service</th>
            <th>CVE ID</th>
            <th>Severity</th>
            <th>CVSS Score</th>
            <th>Type</th>
            <th>Description</th>
            <th>Remediation</th>
        </tr>
"""

    for r in results:
        for v in r["vulnerabilities"]:
            severity = v.get("severity", "Unknown")
            severity_class = severity.lower()
            html += f"""        <tr>
            <td>{r['port']}</td>
            <td>{r['service']}</td>
            <td><strong>{v.get('cve_id', 'N/A')}</strong></td>
            <td><span class="{severity_class}">{severity}</span></td>
            <td>{v.get('cvss_score', 'N/A')}</td>
            <td>{v.get('vuln_type', 'Unknown')}</td>
            <td>{v.get('description', '')[:100]}</td>
            <td>{v.get('remediation', 'N/A')[:80]}</td>
        </tr>
"""

    html += """    </table>
</body>
</html>
"""

    with open(filename, 'w') as f:
        f.write(html)

    return str(filename)


def main():
    parser = argparse.ArgumentParser(
        description="Vulnerability Scanner - Network security assessment tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan default ports (1-1024) on target and save PDF
  python cli.py -t example.com

  # Scan full port range with JSON export
  python cli.py -t 192.168.1.1 -p 1-65535 -f json

  # Quick scan with multiple formats
  python cli.py -t target.local -p 1-1024 -f pdf,json,csv

  # Scan with custom timeout and workers
  python cli.py -t 10.0.0.1 --timeout 2 --workers 200 -p 20-1024
        """
    )

    parser.add_argument('-t', '--target', required=True, help='Target IP or hostname')
    parser.add_argument('-p', '--ports', default='1-65535',
                       help='Port range (e.g., "1-65535", "80,443,8080", "20-1000")')
    parser.add_argument('-f', '--format', default='pdf',
                       help='Output format: pdf, json, csv, html (comma-separated for multiple)')
    parser.add_argument('--timeout', type=float, default=1.5, help='Socket timeout in seconds')
    parser.add_argument('--workers', type=int, default=100, help='Max concurrent workers')
    parser.add_argument('-o', '--output', help='Output directory (default: ./reports)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Parse port range
    try:
        if '-' in args.ports:
            start, end = map(int, args.ports.split('-'))
            port_range = (start, end + 1)
        else:
            ports = [int(p.strip()) for p in args.ports.split(',')]
            port_range = (min(ports), max(ports) + 1)
    except ValueError:
        logger.error("Invalid port format. Use '1-1024' or '80,443,8080'")
        sys.exit(1)

    # Run scan
    logger.info(f"Starting scan of {args.target}")
    results, stats = start_scan(args.target, port_range=port_range,
                                timeout=args.timeout, max_workers=args.workers)

    if not results:
        logger.warning("No open ports found")
        return

    # Export results
    formats = [f.strip() for f in args.format.split(',')]
    for fmt in formats:
        fmt = fmt.lower().strip()
        if fmt == 'pdf':
            filename = generate_pdf_report(args.target, results, stats)
            logger.info(f"PDF report saved: {filename}")
        elif fmt == 'json':
            filename = export_json(results, args.target)
            logger.info(f"JSON report saved: {filename}")
        elif fmt == 'csv':
            filename = export_csv(results, args.target)
            logger.info(f"CSV report saved: {filename}")
        elif fmt == 'html':
            filename = export_html(results, args.target)
            logger.info(f"HTML report saved: {filename}")
        else:
            logger.warning(f"Unknown format: {fmt}")

    logger.info("Scan complete")


if __name__ == '__main__':
    main()
