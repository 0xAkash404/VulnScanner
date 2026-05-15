import json
import os
import re


def load_cve_database():
    """Load CVE database using absolute path to avoid working directory issues."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cve_database.json")
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[CVE-DB] Error loading database: {e}")
        return []


def parse_version(version_str):
    """Parse a version string into a tuple of integers for comparison."""
    if not version_str or version_str == "Unknown":
        return None
    # Extract numeric version parts (e.g., "2.4.49" -> (2, 4, 49))
    match = re.match(r'(\d+(?:\.\d+)*)', version_str.strip())
    if not match:
        return None
    parts = match.group(1).split(".")
    return tuple(int(p) for p in parts)


def version_in_range(version_str, version_range):
    """Check if a version falls within a min-max range (inclusive)."""
    ver = parse_version(version_str)
    if ver is None:
        return False

    min_ver = parse_version(version_range.get("min", "0"))
    max_ver = parse_version(version_range.get("max", "999.999.999"))

    if min_ver is None or max_ver is None:
        return False

    # Pad tuples to same length for comparison
    max_len = max(len(ver), len(min_ver), len(max_ver))
    ver = ver + (0,) * (max_len - len(ver))
    min_ver = min_ver + (0,) * (max_len - len(min_ver))
    max_ver = max_ver + (0,) * (max_len - len(max_ver))

    return min_ver <= ver <= max_ver


def check_vulnerabilities(service, version):
    """Check detected service/version against the CVE database.

    Uses proper version range comparison instead of substring matching.
    Returns list of matching CVE entries.
    """
    db = load_cve_database()
    vulnerabilities = []

    service_lower = service.lower()

    for entry in db:
        entry_service_lower = entry.get("service", "").lower()

        # Flexible service matching: either name is a substring of the other
        if service_lower in entry_service_lower or entry_service_lower in service_lower:

            # Support both old format ("version" field) and new format ("version_range")
            if "version_range" in entry:
                if version_in_range(version, entry["version_range"]):
                    vulnerabilities.append(entry)
            elif "version" in entry:
                # Legacy: exact substring match
                if entry["version"] in version:
                    vulnerabilities.append(entry)

    return vulnerabilities
