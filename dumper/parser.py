import csv
import io
import os
import re
from typing import List, Optional, Tuple

from dumper import IGNORED_FILES


def detect_delimiter(sample_lines: List[str]) -> str:
    delimiters = [',', ';', ':', '\t']
    delimiter_counts = {d: 0 for d in delimiters}

    for line in sample_lines:
        for d in delimiters:
            if d in line:
                delimiter_counts[d] += 1

    most_common_delimiter = max(delimiter_counts, key=delimiter_counts.get)
    return most_common_delimiter if delimiter_counts[most_common_delimiter] > 0 else ','

def parse_line(line: str, delimiter: str) -> Optional[Tuple[str, str]]:
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    reader = csv.reader(io.StringIO(line), delimiter=delimiter, quotechar='"')
    parts = next(reader)

    if len(parts) >= 2:
        email, password = parts[:2]
        email = email.strip()
        password = password.strip()

        # Check for potential inline comment, but only if it's not inside quotes
        comment_start = password.find(' #')
        if comment_start != -1:
            # Count quotes before potential comment to determine if it's inside quotes
            quote_count = password[:comment_start].count('"') % 2
            if quote_count == 0:  # Not inside quotes, so it's a comment
                password = password[:comment_start].strip()

        # Basic email validation
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return (email, password)

    return None

async def parse_file(file_path: str) -> List[Tuple[str, str]]:
    credentials = []
    
    # Check if the file should be ignored
    if os.path.basename(file_path) in IGNORED_FILES:
        return credentials

    try:
        if not os.path.isfile(file_path):
            return credentials  # Silently return empty list for directories or non-existent files

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            sample_lines = [next(file) for _ in range(10) if file]
            delimiter = detect_delimiter(sample_lines)

            file.seek(0)
            for line in file:
                result = parse_line(line, delimiter)
                if result:
                    credentials.append(result)

    except Exception as e:
        # Re-raise the exception with additional context, catch and display as a failed file later on
        raise Exception(f"Error parsing file {file_path}: {str(e)}") from e

    return credentials
