"""
Script to get all files in the client project, excluding library files.
This script walks through the client project directory and returns all files
excluding those in .pio/libdeps and other library directories.
"""

import os
from pathlib import Path


def get_client_files(project_dir):
    """
    Get all files in the client project, excluding library directories.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
    
    Returns:
        List of file paths relative to project_dir
    """
    print("Gonna print client files")
    project_path = Path(project_dir).resolve()
    client_files = []
    
    # Directories to exclude (PlatformIO library and build directories)
    exclude_dirs = {
        '.pio',           # PlatformIO build and library directory
        '.git',           # Git directory
        '.vscode',        # VS Code settings (optional, but common)
        '.idea',          # IDE settings
    }
    
    # Walk through the project directory
    for root, dirs, files in os.walk(project_path):
        # Convert to Path for easier manipulation
        root_path = Path(root)
        
        # Skip if this directory or any parent is in exclude_dirs
        should_skip = False
        for part in root_path.parts:
            if part in exclude_dirs:
                should_skip = True
                break
        
        if should_skip:
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            continue
        
        # Add all files in this directory
        for file in files:
            file_path = root_path / file
            # Get relative path from project root
            try:
                rel_path = file_path.relative_to(project_path)
                client_files.append(str(rel_path))
            except ValueError:
                # Skip if path is not relative (shouldn't happen, but safety check)
                continue
    
    return sorted(client_files)


if __name__ == "__main__":
    # This can be called standalone for testing
    import sys
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        # Default to current directory
        project_dir = os.getcwd()
    
    files = get_client_files(project_dir)
    for f in files:
        print(f)

