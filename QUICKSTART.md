# VulnScanner v2.0 - Quick Start Guide

## ⚡ 60-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run a scan
python cli.py -t example.com

# Done! Report saved to ./reports/
```

---

## 🚀 Common Use Cases

### Scan with Full Port Range (1-65535)
```bash
python cli.py -t target.com
# Scans all ports with default 1.5s timeout, 100 workers
# Reports ETA as it progresses
# Default output: PDF in ./reports/
```

**Expected Time**: ~10-15 minutes depending on network

### Fast Scan (Common Ports Only)
```bash
python cli.py -t target.com -p 80,443,22,21,25,3306,5432
# Scans only 7 specific ports (~5 seconds)
```

### Scan with Multiple Formats
```bash
python cli.py -t target.com -f pdf,json,csv,html
# Generates 4 different report formats
```

### Custom Workers & Timeout
```bash
python cli.py -t target.com --workers 300 --timeout 2.0
# Faster scanning: 300 concurrent threads
# Slower networks: 2.0 second timeout
```

### Verbose Output with ETA
```bash
python cli.py -t target.com -v
# Shows detailed progress and ETA for remaining ports
```

---

## 📊 Report Features

### PDF Report Includes:
- ✅ **Executive Summary** - Quick overview of findings
- ✅ **Risk Distribution** - Table showing Critical/High/Medium/Low counts
- ✅ **Port & Service Summary** - All open ports with versions
- ✅ **Detailed Vulnerabilities** - Full CVE information with CVSS scores
- ✅ **Top Services** - Visual breakdown of services with vulnerabilities
- ✅ **Severity Color-Coding** - Red for Critical, Orange for High

### JSON Report Includes:
```json
{
  "target": "example.com",
  "scan_date": "2026-04-13 14:22:30",
  "total_ports": 65535,
  "open_ports": 12,
  "total_vulnerabilities": 8,
  "critical_count": 2,
  "scan_stats": {
    "scan_time": 635.2,
    "ports_per_second": 103.2
  },
  "ports": [...]
}
```

### CSV Report:
Easy import to Excel/Sheets for analysis and filtering

### HTML Report:
Browser-viewable with color-coded severity levels

---

## 💡 Pro Tips

### 1. Network Scanning (Full Subnet)
```bash
# Requires nmap or similar for subnet discovery
# Then scan individual IPs:
for ip in 192.168.1.{1..254}; do
  python cli.py -t $ip -p 80,443,22 &
done
```

### 2. Scheduled Scans
```bash
# Weekly full scan via cron
0 2 * * 0 cd /path/to/scanner && python cli.py -t prod.example.com -f json -o /reports/weekly/
```

### 3. SIEM Integration
```bash
# Export JSON and send to Splunk/ELK:
python cli.py -t target.com -f json | curl -X POST http://splunk:8088/services/collector \
  -H "Authorization: Splunk YOUR_TOKEN" \
  -d @-
```

### 4. Performance on Slow Networks
```bash
# For high-latency or slow networks:
python cli.py -t target.com --timeout 5.0 --workers 50
# Increase timeout, reduce workers for stability
```

### 5. Quick Vulnerability Check
```bash
# Just check if target has critical vulnerabilities:
python cli.py -t target.com -f json | grep -i critical
```

---

## ⏱️ Timing Reference

| Port Range | Workers | Timeout | Est. Time |
|-----------|---------|---------|-----------|
| 80,443 | N/A | 1.5s | 5s |
| 1-1024 | 100 | 1.5s | 20-30s |
| 1-10000 | 100 | 1.5s | 2-3 min |
| 1-65535 | 100 | 1.5s | 10-15 min |
| 1-65535 | 300 | 1.5s | 5-8 min |

*Times vary based on network latency, target responsiveness, and firewall rules*

---

## 🔍 Understanding Results

### Risk Score
- **0-3.9** (Low) - Informational findings
- **4.0-6.9** (Medium) - Should be addressed in regular patch cycle
- **7.0-8.9** (High) - Significant risk, prioritize patching
- **9.0-10.0** (Critical) - Immediate action required

### CVSS Score
- Industry-standard severity rating (0-10 scale)
- Lower scores = less impact
- Helps prioritize remediation

### Example Output
```
[Scanner] [100%] Scanned 65535/65535 ports | Found 8 open | ETA: 0s
[Scanner] ✓ Scan complete in 642.5s
[Scanner] Results: 8 open ports, 4 vulnerabilities
[Scanner]  - Critical: 1 | High: 2
[Scanner]  - Speed: 102 ports/sec
```

---

## 🛠️ Web Dashboard

### Start Dashboard
```bash
python app.py
# Open http://127.0.0.1:5000
```

### Features:
- Point-and-click target entry
- Custom port range selection
- Real-time results
- PDF download

---

## 🔐 Authorization & Legal

⚠️ **IMPORTANT**: Only scan systems you own or have explicit written permission to test

Using this tool without authorization is illegal in most jurisdictions.

---

## 🆘 Troubleshooting

### "Could not resolve target"
```bash
# Check DNS / network connectivity
ping example.com
nslookup example.com
```

### Very Slow Scan
```bash
# Try with fewer workers on slow networks:
python cli.py -t target.com --workers 50

# Or just scan common ports:
python cli.py -t target.com -p 80,443,22,21,25,3306,5432,8080
```

### "Permission denied" on Linux
```bash
# May need sudo for certain ports:
sudo python cli.py -t target.com
```

### Out of Memory
```bash
# Reduce workers for large port ranges:
python cli.py -t target.com -p 1-65535 --workers 50
```

---

## 📞 Support

- **Full Docs**: Read `README.md`
- **Improvements**: See `IMPROVEMENTS.md`
- **Issues**: GitHub Issues (when available)

---

## 🎯 Next Steps

1. **Try a test scan**: `python cli.py -t 127.0.0.1`
2. **Check the reports**: Open `./reports/` directory
3. **Customize config**: Edit `config.json`
4. **Schedule scans**: Add to cron jobs
5. **Integrate**: Use JSON export in your security tools

---

**Happy scanning! 🚀**
