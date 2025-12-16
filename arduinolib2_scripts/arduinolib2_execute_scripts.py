"""
Script to execute client file processing.
This script imports get_client_files and processes the client project files.
"""

try:
    from arduinolib1_core.arduinolib1_get_client_files import get_client_files
    HAS_ARDUINOLIB1 = True
except ImportError:
    print("Warning: Could not import arduinolib1_core.arduinolib1_get_client_files")
    print("         Some features may be unavailable.")
    HAS_ARDUINOLIB1 = False
    # Create a dummy function to avoid errors
    def get_client_files(*args, **kwargs):
        return []

def execute_scripts(project_dir, library_dir):
    """
    Execute the scripts to process client files.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
        library_dir: Path to the library directory
    """
    if not HAS_ARDUINOLIB1:
        print("Skipping file processing - arduinolib1_core not available")
        return

    print(f"\nproject_dir: {project_dir}")
    print(f"library_dir: {library_dir}")

    if project_dir:
        client_files = get_client_files(project_dir, file_extensions=['.h', '.cpp'])
        print(f"\nFound {len(client_files)} files in client project:")
        print("=" * 60)
        for file in client_files:
            print(file)
        print("=" * 60)

    if library_dir:
        library_files = get_client_files(library_dir, skip_exclusions=True)
        print(f"\nFound {len(library_files)} files in library:")
        print("=" * 60)
        for file in library_files:
            print(file)
        print("=" * 60)
