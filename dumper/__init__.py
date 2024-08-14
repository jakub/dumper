"""Dumper - A credential parsing and normalization tool."""

__version__ = "0.1.0"

# List of system files to ignore
IGNORED_FILES = {
    '.DS_Store',  # macOS
    'Thumbs.db',  # Windows
    'desktop.ini',  # Windows
    '.directory',  # KDE
    '.Trash-1000',  # Linux
    '.Spotlight-V100',  # macOS
    '.fseventsd',  # macOS
    '.TemporaryItems',  # macOS
    '$RECYCLE.BIN',  # Windows
    'System Volume Information',  # Windows
}
