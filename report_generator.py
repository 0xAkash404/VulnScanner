"""
Professional PDF Report Generator with Charts and Graphs
Generates comprehensive vulnerability scan reports with visualizations
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.platypus import SimpleDocTemplate, Table, Image as RLImage
import os
from utils import get_timestamp
from io import BytesIO
import tempfile


def create_severity_pie_chart():
    """Create a pie chart showing vulnerability distribution by severity."""
    drawing = Drawing(400, 300)
    pie = Pie()
    pie.data = [5, 15, 25, 55]  # Placeholder, will be set in report
    pie.labels = ['Low', 'Medium', 'High', 'Critical']
    pie.slices.strokeWidth = 0.5
    pie.slices[0].fillColor = colors.HexColor("#27ae60")  # Green
    pie.slices[1].fillColor = colors.HexColor("#f39c12")  # Orange
    pie.slices[2].fillColor = colors.HexColor("#e67e22")  # Dark Orange
    pie.slices[3].fillColor = colors.HexColor("#e74c3c")  # Red

    drawing.add(pie, x=60, y=30)
    return drawing


def generate_vulnerability_severity_data(results):
    """Extract vulnerability severity distribution."""
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for r in results:
        for v in r["vulnerabilities"]:
            severity = v.get("severity", "Unknown")
            if severity in severity_counts:
                severity_counts[severity] += 1

    return severity_counts


def generate_service_vulnerability_chart(results):
    """Create chart showing vulnerabilities by service."""
    service_vulns = {}

    for r in results:
        service = r["service"]
        if service not in service_vulns:
            service_vulns[service] = 0
        service_vulns[service] += len(r["vulnerabilities"])

    # Sort by vulnerability count and take top 10
    top_services = sorted(service_vulns.items(), key=lambda x: x[1], reverse=True)[:10]

    drawing = Drawing(600, 300)
    chart = VerticalBarChart()
    chart.data = [[count for _, count in top_services]]
    chart.categoryAxis.categoryNames = [service[:15] for service, _ in top_services]
    chart.width = 550
    chart.height = 250
    chart.title = "Top Services with Vulnerabilities"

    drawing.add(chart, x=25, y=30)
    return drawing


def generate_pdf_report(target, results, stats=None):
    """Generate comprehensive PDF report with charts and graphs.

    Args:
        target: Target hostname/IP
        results: List of scan results
        stats: Dictionary with scan statistics

    Returns:
        Path to generated PDF file
    """
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Sanitize target for filename
    safe_target = "".join(c if c.isalnum() or c in ".-_" else "_" for c in target)
    filename = os.path.join(reports_dir, f"scan_report_{safe_target}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    # ===== PAGE 1: TITLE & SUMMARY =====
    elements.append(Paragraph("VULNERABILITY SCAN REPORT", title_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Header info
    header_data = [
        ["Target:", target],
        ["Scan Date:", get_timestamp()],
        ["Total Ports Scanned:", f"{stats.get('total_ports', 'N/A') if stats else 'N/A'}"],
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#3498db")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Executive Summary
    total_vulns = sum(len(r["vulnerabilities"]) for r in results)
    critical_count = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "Critical")
    high_count = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "High")
    medium_count = sum(1 for r in results for v in r["vulnerabilities"] if v.get("severity") == "Medium")

    elements.append(Paragraph("Executive Summary", heading_style))

    summary_text = f"""
    <b>Open Ports:</b> {len(results)}<br/>
    <b>Total Vulnerabilities:</b> {total_vulns}<br/>
    <b>Critical:</b> <font color="red">{critical_count}</font> |
    <b>High:</b> <font color="orange">{high_count}</font> |
    <b>Medium:</b> <font color="#f39c12">{medium_count}</font>
    """

    if stats:
        summary_text += f"""<br/>
    <b>Scan Time:</b> {stats.get('scan_time', 0):.1f}s<br/>
    <b>Scanning Speed:</b> {stats.get('ports_per_second', 0):.0f} ports/sec
    """

    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Risk Distribution
    elements.append(Paragraph("Risk Distribution", heading_style))

    severity_data = generate_vulnerability_severity_data(results)
    risk_summary_data = [
        ["Severity", "Count", "Percentage"],
        ["Critical", str(severity_data["Critical"]), f"{(severity_data['Critical']/max(total_vulns, 1)*100):.1f}%"],
        ["High", str(severity_data["High"]), f"{(severity_data['High']/max(total_vulns, 1)*100):.1f}%"],
        ["Medium", str(severity_data["Medium"]), f"{(severity_data['Medium']/max(total_vulns, 1)*100):.1f}%"],
        ["Low", str(severity_data["Low"]), f"{(severity_data['Low']/max(total_vulns, 1)*100):.1f}%"],
    ]

    risk_table = Table(risk_summary_data, colWidths=[1.5*inch, 1*inch, 1.5*inch])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(risk_table)
    elements.append(PageBreak())

    # ===== PAGE 2: PORT & SERVICE SUMMARY =====
    elements.append(Paragraph("Port & Service Summary", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Port/Service table
    port_data = [["Port", "Service", "Version", "Vulns", "Risk Score", "Top Severity"]]
    for r in results:
        top_severity = "None"
        if r["vulnerabilities"]:
            severities = [v.get("severity") for v in r["vulnerabilities"]]
            if "Critical" in severities:
                top_severity = "Critical"
            elif "High" in severities:
                top_severity = "High"
            elif "Medium" in severities:
                top_severity = "Medium"

        port_data.append([
            str(r["port"]),
            r["service"][:20],
            r["version"][:20],
            str(r["vuln_count"]),
            str(r["risk_score"]),
            top_severity
        ])

    port_table = Table(port_data, colWidths=[0.7*inch, 1*inch, 1.2*inch, 0.6*inch, 0.8*inch, 1*inch])
    port_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f81f7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(port_table)
    elements.append(PageBreak())

    # ===== PAGE 3: VULNERABILITY DETAILS =====
    vuln_rows = [["Port", "Service", "CVE ID", "Severity", "CVSS", "Type", "Remediation"]]

    for r in results:
        for v in r["vulnerabilities"]:
            severity = v.get("severity", "Unknown")
            # Color code severity
            severity_color = "#27ae60"  # Green
            if severity == "Critical":
                severity_color = "#e74c3c"
            elif severity == "High":
                severity_color = "#e67e22"
            elif severity == "Medium":
                severity_color = "#f39c12"

            vuln_rows.append([
                str(r["port"]),
                r["service"][:15],
                v.get("cve_id", "N/A"),
                f'<font color="{severity_color}">{severity}</font>',
                str(v.get("cvss_score", "N/A")),
                v.get("vuln_type", "Unknown")[:15],
                v.get("remediation", "")[:30],
            ])

    if len(vuln_rows) > 1:
        elements.append(Paragraph("Detailed Vulnerabilities", heading_style))
        elements.append(Spacer(1, 0.1 * inch))

        vuln_table = Table(vuln_rows, colWidths=[0.6*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.6*inch, 1*inch, 1.4*inch])
        vuln_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("FONTSIZE", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ]))
        elements.append(vuln_table)
    else:
        elements.append(Paragraph("✓ No vulnerabilities found.", styles["Normal"]))

    # Build PDF
    doc.build(elements)
    return filename
