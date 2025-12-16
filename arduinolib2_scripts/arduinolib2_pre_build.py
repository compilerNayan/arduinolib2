# Print message immediately when script is loaded
print("Hello from library number 2")

# Import PlatformIO environment first
Import("env")

import sys
import os
from pathlib import Path


def get_library_dir():
    """
    Find the arduinolib2_scripts directory by searching up the directory tree.
    
    Returns:
        Path: Path to the arduinolib2_scripts directory
        
    Raises:
        ImportError: If the directory cannot be found
    """
    cwd = Path(os.getcwd())
    current = cwd
    for _ in range(10):  # Search up to 10 levels
        potential = current / "arduinolib2_scripts"
        if potential.exists() and potential.is_dir():
            print(f"✓ Found library path by searching up directory tree: {potential}")
            return potential
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    raise ImportError("Could not find arduinolib2_scripts directory")


def get_project_dir():
    """
    Get the project directory from PlatformIO environment.
    
    Returns:
        str: Path to the project directory, or None if not found
    """
    project_dir = env.get("PROJECT_DIR", None)
    if project_dir:
        print(f"\nClient project directory: {project_dir}")
    else:
        print("Warning: Could not determine PROJECT_DIR from environment")
    return project_dir


# Get library directory and add it to Python path
library_dir = get_library_dir()
sys.path.insert(0, str(library_dir))

# Get project directory
project_dir = get_project_dir()

# Import and execute scripts
from arduinolib2_execute_scripts import execute_scripts
execute_scripts(project_dir)

