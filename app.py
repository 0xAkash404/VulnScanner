from flask import Flask, render_template, request, jsonify
from scanner import start_scan
from report_generator import generate_pdf_report
from utils import resolve_target
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


@app.route("/", methods=["GET", "POST"])
def dashboard():
    scan_results = []
    error = None
    info = None

    try:
        if request.method == "POST":
            target = request.form.get("target", "").strip()
            port_range_input = request.form.get("port_range", "1-1024").strip()

            # Validate target
            if not target:
                error = "Target is required"
            elif len(target) > 255:
                error = "Target is too long (max 255 characters)"
            elif not (resolve_target(target)):
                error = f"Could not resolve target: {target}"
            else:
                try:
                    # Parse port range
                    if '-' in port_range_input:
                        parts = port_range_input.split('-')
                        if len(parts) != 2:
                            raise ValueError("Invalid port range format")
                        start_port = int(parts[0].strip())
                        end_port = int(parts[1].strip())
                    else:
                        ports = [int(p.strip()) for p in port_range_input.split(',')]
                        start_port = min(ports)
                        end_port = max(ports)

                    if start_port < 1 or end_port > 65535 or start_port > end_port:
                        error = "Invalid port range. Ports must be between 1-65535"
                    else:
                        # Run scan
                        port_range = (start_port, end_port + 1)
                        logger.info(f"Starting scan of {target} ({port_range})")
                        scan_results, scan_stats = start_scan(target, port_range=port_range)

                        if scan_results:
                            try:
                                pdf_file = generate_pdf_report(target, scan_results, scan_stats)
                                total_vulns = sum(len(r["vulnerabilities"]) for r in scan_results)
                                info = f"Scan complete: {len(scan_results)} open ports, {total_vulns} vulnerabilities found. Report: {pdf_file}"
                                logger.info(info)
                            except Exception as e:
                                logger.error(f"Error generating PDF: {e}")
                                error = "Scan complete but PDF generation failed"
                        else:
                            info = "Scan complete: No open ports found in the specified range"

                except ValueError as e:
                    error = f"Invalid port specification: {str(e)}"
                except Exception as e:
                    error = f"Scan error: {str(e)}"
                    logger.error(f"Scan failed: {traceback.format_exc()}")

        return render_template("dashboard.html", results=scan_results, error=error, info=info)

    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        return render_template("dashboard.html", results=[], error=f"An unexpected error occurred: {str(e)}")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    """API endpoint for JSON-based scanning."""
    try:
        data = request.json
        target = data.get("target", "").strip()
        port_range_str = data.get("port_range", "1-1024")

        if not target:
            return jsonify({"error": "Target is required"}), 400

        # Parse ports
        try:
            if '-' in port_range_str:
                start, end = map(int, port_range_str.split('-'))
                port_range = (start, end + 1)
            else:
                ports = [int(p.strip()) for p in port_range_str.split(',')]
                port_range = (min(ports), max(ports) + 1)
        except ValueError:
            return jsonify({"error": "Invalid port format"}), 400

        # Run scan
        results, stats = start_scan(target, port_range=port_range)

        return jsonify({
            "target": target,
            "open_ports": len(results),
            "total_vulnerabilities": sum(len(r["vulnerabilities"]) for r in results),
            "stats": stats,
            "results": results
        })

    except Exception as e:
        logger.error(f"API scan error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    logger.info("Starting Vulnerability Scanner Web Interface...")
    app.run(host="127.0.0.1", port=5000, debug=False)
