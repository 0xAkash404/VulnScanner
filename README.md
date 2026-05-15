# Vulnerability Scanner v2.0

A production-ready, comprehensive vulnerability scanner for network security assessment. Performs port scanning, service detection, banner grabbing, and vulnerability matching against an extensive CVE database.

## Features

### Core Capabilities
- **Port Scanning**: Fast multi-threaded port scanning (1-65535+ configurable)
- **Service Detection**: 40+ service patterns with version extraction
- **Banner Grabbing**: Protocol-specific banner collection (SSH, FTP, HTTP, SMTP, MySQL, Redis, MongoDB, etc.)
- **CVE Database**: 100+ known vulnerabilities with CVSS scoring
- **Risk Scoring**: Accurate CVSS-based vulnerability scoring
- **Progress Tracking**: Real-time scan progress updates

### Output Formats
- **PDF Reports** - Professional vulnerability reports with summaries and details
- **JSON Export** - Machine-readable results for integration with SIEM/automation
- **CSV Export** - Spreadsheet-compatible format for analysis
- **HTML Reports** - Browser-viewable formatted reports
- **Web Dashboard** - Flask-based interactive dashboard

### Production Features
- **Configuration Management** - JSON-based configuration files
- **Error Handling** - Robust error handling and validation
- **Logging** - Comprehensive logging infrastructure
- **CLI Tool** - Command-line interface for automation and integration
- **Parallel Processing** - Configurable worker threads for speed
- **Custom Timeouts** - Adjustable socket timeouts for slow networks

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/yourusername/vulnscanner.git
cd vulnscanner

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### System Requirements
- Python 3.7+
- pip or conda
- Network access to targets
- ~50MB disk space

## Usage

### Web Interface

```bash
python app.py
# Navigate to http://127.0.0.1:5000
```

### Command-Line Interface

#### Basic Scan
```bash
python cli.py -t example.com
# Scans ports 1-1024, exports as PDF
```

#### Custom Port Range
```bash
python cli.py -t 192.168.1.1 -p 1-65535
# Full port range scan

python cli.py -t target.local -p 80,443,8080,8443
# Specific ports only
```

#### Multiple Export Formats
```bash
python cli.py -t 10.0.0.1 -f pdf,json,csv,html
# Generates all four report formats
```

#### Performance Tuning
```bash
python cli.py -t 192.168.1.100 --workers 200 --timeout 2.0 -p 1-10000
# Increase workers for faster scanning
# Adjust timeout for slower networks
```

#### Verbose Output
```bash
python cli.py -t target.example.com -v
# Shows detailed progress and logging
```

### Configuration

Create `config.json` in the project directory:

```json
{
  "scanner": {
    "timeout": 1.5,
    "max_workers": 100,
    "port_range": [1, 1024]
  },
  "reporting": {
    "formats": ["pdf", "json"],
    "output_dir": "reports"
  },
  "logging": {
    "level": "INFO",
    "file": "scanner.log"
  }
}
```

## CVE Database

The scanner includes 100+ documented vulnerabilities covering:

- Apache HTTP Server (2.4.x)
- Nginx (0.6 - 1.25.x)
- OpenSSH (5.0 - 9.x)
- OpenSSL (1.0.1 - 3.x)
- MySQL/MariaDB (5.x - 10.x)
- PostgreSQL (9.3 - 16.x)
- Redis (2.0 - 7.x)
- Microsoft IIS (7.0 - 10.x)
- PHP (5.0 - 8.x)
- FTP Services (vsftpd, ProFTPD, Pure-FTPd)
- Mail Services (Postfix, Exim, Dovecot, Sendmail)
- App Servers (Tomcat, Jetty, JBoss, WildFly)
- Database Services (MongoDB, Memcached)
- And many more...

Each entry includes:
- CVE ID and severity level
- CVSS Score (3.1)
- Detailed description
- Affected version ranges
- Recommended remediation steps
- References and citations

## Vulnerability Severity Levels

- **Critical** (CVSS 9.0-10.0) - Immediate action required
- **High** (CVSS 7.0-8.9) - High priority patching
- **Medium** (CVSS 4.0-6.9) - Regular patch cycle
- **Low** (CVSS 0.1-3.9) - Monitor and address

## Report Examples

### PDF Report
Includes executive summary, port/service listing, vulnerability details with CVSS scores, and remediation guidance.

### JSON Report
```json
{
  "target": "example.com",
  "scan_date": "2026-04-13 14:22:30",
  "total_ports": 12,
  "total_vulnerabilities": 8,
  "critical_count": 2,
  "high_count": 4,
  "ports": [...]
}
```

### CSV Report
Spreadsheet format with columns: Port, Service, Version, CVE ID, Severity, CVSS Score, Type, Description

## Performance

Typical scanning times (on modern hardware):

| Port Range | Threads | Time |
|-----------|---------|------|
| 1-1024    | 100     | 30-60s |
| 1-10000   | 200     | 2-3m |
| 1-65535   | 300     | 8-12m |

*Times vary based on network latency and target responsiveness*

## Accuracy & Limitations

### Strengths
- ✅ Accurate service detection via banner analysis
- ✅ Comprehensive vulnerability database
- ✅ CVSS-based risk scoring
- ✅ Support for major services and platforms
- ✅ Version range matching for precise detection

### Limitations
- ⚠️ Requires open ports (passive detection not available)
- ⚠️ Limited to TCP protocols
- ⚠️ May not detect obscured banners
- ⚠️ CVE database is periodically updated (not real-time)
- ⚠️ Network access restrictions may affect scanning

## Security Considerations

### Authorization
- **Only scan systems you own or have explicit permission to test**
- Unauthorized network scanning may be illegal
- Maintain audit trails of all scanning activities
- Use in authorized penetration testing contexts only

### Network Impact
- 100 concurrent connections per scan
- ~10-50 KB per port scanned
- Minimal CPU impact
- Consider network load during large scans

### Data Protection
- Reports contain sensitive vulnerability information
- Store reports in secure locations
- Restrict report access to authorized personnel
- Follow organizational data retention policies

## Troubleshooting

### Slow Scanning
```bash
# Increase workers and adjust timeout
python cli.py -t target.com --workers 300 --timeout 0.5
```

### Connection Timeouts
```bash
# Increase timeout for slow/distant targets
python cli.py -t target.com --timeout 3.0
```

### SSL/TLS Errors
The scanner handles self-signed certificates gracefully. For HTTPS ports, version detection may be limited if banners aren't exposed.

### Large Port Ranges
For scanning 1-65535, allocate sufficient time (10-15 minutes) and system resources.

## Advanced Usage

### Integration with Automation
```bash
#!/bin/bash
for target in targets.txt; do
  python cli.py -t $target -f json -o /reports/$(date +%Y%m%d)/
done
```

### SIEM Integration
Export as JSON and integrate with Splunk, ELK, or other SIEM platforms for centralized vulnerability tracking.

### Scheduled Scanning
```bash
# Crontab entry for weekly scanning
0 2 * * 0 cd /path/to/vulnscanner && python cli.py -t 192.168.1.0/24 -f all
```

## Development

### Dependencies
- Python 3.7+
- flask (web interface)
- reportlab (PDF generation)
- requests (HTTP client)

### Project Structure
```
vulnscanner/
├── app.py                 # Flask web application
├── cli.py                 # Command-line interface
├── scanner.py             # Core scanning engine
├── service_detector.py    # Service detection logic
├── banner_grabber.py      # Banner collection
├── cve_checker.py         # Vulnerability matching
├── report_generator.py    # PDF report generation
├── config.py              # Configuration management
├── utils.py               # Utility functions
├── data/
│   └── cve_database.json  # CVE vulnerability database
├── reports/               # Generated reports
├── config.json            # Configuration file
└── requirements.txt       # Python dependencies
```

## Contributing

Contributions welcome! Areas for enhancement:
- Additional CVE database entries
- UDP/ICMP scanning support
- Web server module detection
- Custom vulnerability rules
- Performance optimizations
- Additional report formats

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is provided for authorized security testing and educational purposes only. Users are responsible for ensuring all scanning is authorized and legal. The authors assume no liability for misuse or damage caused by this tool.

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/yourusername/vulnscanner/issues
- Documentation: https://github.com/yourusername/vulnscanner/wiki

## Version History

### v2.0 (2026-04-13)
- Expanded CVE database to 100+ entries with CVSS scores
- Added multi-format export (JSON, CSV, HTML, PDF)
- Created comprehensive CLI interface
- Added configuration file support
- Improved service detection with 40+ patterns
- Enhanced error handling and logging
- Added progress tracking
- Performance optimizations

### v1.0 (Initial)
- Basic port scanning
- Service detection
- Banner grabbing
- CVE matching
- PDF report generation
- Web dashboard
#   V u l n S c a n n e r  
 