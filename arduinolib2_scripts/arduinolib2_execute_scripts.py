"""
Script to execute client file processing.
This script imports get_client_files and processes the client project files.
"""

from arduinolib2_core.get_client_files import get_client_files


def execute_scripts(project_dir):
    """
    Execute the scripts to process client files.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
    """
    if project_dir:
        client_files = get_client_files(project_dir)
        print(f"\nFound {len(client_files)} files in client project:")
        print("=" * 60)
        for file in client_files:
            print(file)
        print("=" * 60)

