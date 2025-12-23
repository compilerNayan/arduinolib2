# Print message immediately when script is loaded
print("Hello from library number 2")

# Import PlatformIO environment first (if available)
env = None
try:
    Import("env")
except NameError:
    # Not running in PlatformIO environment (e.g., running from CMake)
    print("Note: Not running in PlatformIO environment - some features may be limited")
    # Create a mock env object for CMake builds
    class MockEnv:
        def get(self, key, default=None):
            return default
    env = MockEnv()

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
    Get the project directory from PlatformIO environment or CMake environment.
    
    Returns:
        str: Path to the project directory, or None if not found
    """
    # Try PlatformIO environment first
    project_dir = None
    if env:
        project_dir = env.get("PROJECT_DIR", None)
    
    # If not found, try CMake environment variable
    if not project_dir:
        project_dir = os.environ.get("CMAKE_PROJECT_DIR", None)
    
    if project_dir:
        print(f"\nClient project directory: {project_dir}")
    else:
        print("Warning: Could not determine PROJECT_DIR from environment")
    return project_dir


def find_library_scripts(scripts_dir_name):
    """
    Find a library scripts directory by searching from current directory and project directory.
    
    Args:
        scripts_dir_name: Name of the scripts directory to find (e.g., "arduinolib1_scripts")
    
    Returns:
        Path: Path to the scripts directory, or None if not found
    """
    # Derive library source directory name from scripts directory name
    # e.g., "arduinolib1_scripts" -> "arduinolib1-src"
    if scripts_dir_name.endswith("_scripts"):
        lib_name = scripts_dir_name[:-8]  # Remove "_scripts" suffix
        lib_src_name = f"{lib_name}-src"
    else:
        # Fallback: assume scripts_dir_name is the library name
        lib_src_name = f"{scripts_dir_name}-src"
    
    search_paths = []
    
    # Add current working directory
    search_paths.append(Path(os.getcwd()))
    
    # Add project directory if available
    project_dir = get_project_dir()
    if project_dir:
        project_path = Path(project_dir)
        search_paths.append(project_path)
        
        # Check build/_deps/{lib_src_name}/{scripts_dir_name} from project directory
        build_deps = project_path / "build" / "_deps" / lib_src_name / scripts_dir_name
        if build_deps.exists() and build_deps.is_dir():
            print(f"✓ Found {scripts_dir_name} (CMake from project): {build_deps}")
            return build_deps
    
    # Add library directory (parent of arduinolib2_scripts)
    library_scripts_dir = get_library_dir()
    library_dir = library_scripts_dir.parent
    search_paths.append(library_dir)
    
    # If we're in a CMake build, check sibling directory ({lib_src_name} next to arduinolib2-src)
    if "arduinolib2-src" in str(library_dir) or "_deps" in str(library_dir):
        # We're in a CMake FetchContent location, check sibling
        parent_deps = library_dir.parent
        if parent_deps.exists() and parent_deps.name == "_deps":
            lib_src = parent_deps / lib_src_name / scripts_dir_name
            if lib_src.exists() and lib_src.is_dir():
                print(f"✓ Found {scripts_dir_name} (CMake sibling): {lib_src}")
                return lib_src
            # Also check if {lib_src_name} exists but scripts might be in root
            lib_root = parent_deps / lib_src_name
            if lib_root.exists():
                lib_scripts = lib_root / scripts_dir_name
                if lib_scripts.exists() and lib_scripts.is_dir():
                    print(f"✓ Found {scripts_dir_name} (CMake sibling root): {lib_scripts}")
                    return lib_scripts
    
    # Search in each path and their parent directories
    for start_path in search_paths:
        current = start_path.resolve()
        for _ in range(10):  # Search up to 10 levels
            # Check for {scripts_dir_name} in current directory
            potential = current / scripts_dir_name
            if potential.exists() and potential.is_dir():
                print(f"✓ Found {scripts_dir_name}: {potential}")
                return potential
            
            # Check in build/_deps/{lib_src_name}/ (CMake FetchContent location)
            deps_path = current / "build" / "_deps" / lib_src_name / scripts_dir_name
            if deps_path.exists() and deps_path.is_dir():
                print(f"✓ Found {scripts_dir_name} (CMake): {deps_path}")
                return deps_path
            
            # Check in .pio/libdeps/ (PlatformIO location)
            pio_path = current / ".pio" / "libdeps"
            if pio_path.exists():
                for lib_dir in pio_path.iterdir():
                    lib_scripts_path = lib_dir / scripts_dir_name
                    if lib_scripts_path.exists() and lib_scripts_path.is_dir():
                        print(f"✓ Found {scripts_dir_name} (PlatformIO): {lib_scripts_path}")
                        return lib_scripts_path
            
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
    
    print(f"Warning: Could not find {scripts_dir_name} directory")
    return None


# Get library scripts directory and add it to Python path
library_scripts_dir = get_library_dir()
sys.path.insert(0, str(library_scripts_dir))

# Find and add arduinolib0_scripts to Python path
arduinolib0_scripts_dir = find_library_scripts("arduinolib0_scripts")
if arduinolib0_scripts_dir:
    sys.path.insert(0, str(arduinolib0_scripts_dir))

# Find and add arduinolib0_scripts to Python path
arduinolib1_scripts_dir = find_library_scripts("arduinolib1_scripts")
if arduinolib1_scripts_dir:
    sys.path.insert(0, str(arduinolib1_scripts_dir))

# Get library root directory (parent of arduinolib2_scripts)
library_dir = library_scripts_dir.parent

# Get project directory
project_dir = get_project_dir()

# Import and execute scripts
from arduinolib2_execute_scripts import execute_scripts
execute_scripts(project_dir, library_dir)

