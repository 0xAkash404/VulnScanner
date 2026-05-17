# Vulnerability Scanner

A Python-based network security scanner for discovering open ports, identifying services, grabbing banners, and matching findings against a CVE database.

## Features
- Fast multi-threaded port scanning
- Service and version detection
- Banner grabbing for common protocols
- CVE matching with CVSS-based risk scoring
- PDF, JSON, CSV, and HTML report export
- CLI workflow with a Flask web entry point

## Quick Start
Install dependencies:

```powershell
pip install -r requirements.txt
```

Run a basic scan:

```powershell
python cli.py -t example.com
```

Run the web entry point:

```powershell
python app.py
```

## CLI Usage
```powershell
python cli.py -t <target> [options]
```

### Common Options
| Option | Description |
|---|---|
| `-t`, `--target` | Target IP or hostname |
| `-p`, `--ports` | Port range or list of ports |
| `-f`, `--format` | Output format: `pdf`, `json`, `csv`, `html` |
| `--timeout` | Socket timeout in seconds |
| `--workers` | Maximum concurrent workers |
| `-o`, `--output` | Output directory for reports |
| `-v`, `--verbose` | Enable verbose logging |

### Examples
Default scan:

```powershell
python cli.py -t example.com
```

Custom port range:

```powershell
python cli.py -t 192.168.1.10 -p 1-65535
```

Specific ports:

```powershell
python cli.py -t target.local -p 80,443,8080,8443
```

Multiple report formats:

```powershell
python cli.py -t 10.0.0.5 -f pdf,json,csv,html
```

Performance tuning:

```powershell
python cli.py -t 192.168.1.100 --workers 200 --timeout 2.0 -p 1-10000
```

Verbose output:

```powershell
python cli.py -t target.example.com -v
```

## Output Formats
- **PDF** — formatted report for sharing
- **JSON** — machine-readable output
- **CSV** — spreadsheet-friendly export
- **HTML** — browser-friendly report

## Configuration
The scanner supports a `config.json` file for settings such as timeouts, worker counts, logging, and output preferences.

## Project Structure
- `cli.py` — command-line interface
- `app.py` — Flask web entry point
- `scanner.py` — scanning engine
- `service_detector.py` — service/version detection
- `banner_grabber.py` — banner collection helpers
- `cve_checker.py` — vulnerability matching logic
- `report_generator.py` — PDF report generation
- `config.py` — configuration helpers
- `utils.py` — shared utility functions
- `requirements.txt` — Python dependencies

## Safety Notice
Only scan systems you own or have explicit permission to test. Unauthorized network scanning may be illegal.

## License
MIT License
