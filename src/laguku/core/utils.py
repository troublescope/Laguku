import re
from typing import List

def sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be used as a safe filename while preserving readability.
    """
    if not name:
        return "Unknown"
    sanitized = re.sub(r'[<>:"/\\|?*]', ' ', name)
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized.strip('. ') if sanitized else "Unknown"

def extract_title_version(title: str) -> tuple[str, str]:
    """
    Splits a title into its main name and a version/suffix.
    Example: "Evaluasi - Radio Edit" -> ("Evaluasi", "Radio Edit")
    """
    version = ""
    clean_title = title

    # Keywords that indicate a version/suffix
    keywords = ["live", "remix", "edit", "version", "remake", "session", "acoustic", "cover", "reprise"]
    pattern = "|".join(keywords)

    # 1. Look for dash-based suffixes: "Title - Suffix"
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        if re.search(pattern, parts[1], re.IGNORECASE):
            clean_title = parts[0]
            version = parts[1]

    # 2. Look for parentheses/brackets: "Title (Suffix)"
    match = re.search(r'[\(\[](.*?(?:' + pattern + r').*?)[\)\]]', clean_title, re.IGNORECASE)
    if match:
        version = match.group(1)
        clean_title = clean_title.replace(match.group(0), "").strip()

    return clean_title.strip(), version.strip()

def build_filename(metadata, pattern: str = "{title} - {artist}{version}") -> str:
    """
    Builds a filename based on metadata and a template pattern.
    Handles the {version} token by wrapping it in parentheses if found.
    """
    raw_title, version_str = extract_title_version(metadata.title)
    
    artist = sanitize_filename(metadata.artist)
    title = sanitize_filename(raw_title)
    album = sanitize_filename(metadata.album or "Unknown Album")
    
    # If version exists, wrap it in parentheses for the {version} token
    version = f" ({sanitize_filename(version_str)})" if version_str else ""
    
    filename = pattern.replace("{artist}", artist).replace("{title}", title).replace("{album}", album).replace("{version}", version)
    
    return sanitize_filename(filename)
