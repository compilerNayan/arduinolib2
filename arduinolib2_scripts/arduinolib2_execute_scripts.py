"""
Script to execute client file processing.
This script imports get_client_files and processes the client project files.
"""

import os
import sys
import subprocess
from pathlib import Path

# Import debug utility
try:
    from debug_utils import debug_print
except ImportError:
    # Fallback if debug_utils not found - create a no-op function
    def debug_print(*args, **kwargs):
        pass

try:
    from arduinolib0_core.arduinolib0_get_client_files import get_client_files
    HAS_ARDUINOLIB0 = True
except ImportError:
    debug_print("Warning: Could not import arduinolib0_core.arduinolib0_get_client_files")
    debug_print("         Some features may be unavailable.")
    HAS_ARDUINOLIB0 = False
    # Create a dummy function to avoid errors
    def get_client_files(*args, **kwargs):
        return []

def execute_scripts(project_dir, library_dir, all_libs=None, library_scripts_dir=None):
    """
    Execute the scripts to process client files.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
        library_dir: Path to the library directory
        all_libs: Dictionary with library directories (from get_all_library_dirs)
        library_scripts_dir: Path to the arduinolib2_scripts directory (optional, will be derived from library_dir if not provided)
    """
    # Process client files if arduinolib0 is available
    if HAS_ARDUINOLIB0:
        debug_print(f"\nproject_dir: {project_dir}")
        debug_print(f"library_dir: {library_dir}")

        if project_dir:
            client_files = get_client_files(project_dir, file_extensions=['.h', '.cpp'])
            debug_print(f"\nFound {len(client_files)} files in client project:")
            debug_print("=" * 60)
            for file in client_files:
                debug_print(file)
            debug_print("=" * 60)

        if library_dir:
            library_files = get_client_files(library_dir, skip_exclusions=True)
            debug_print(f"\nFound {len(library_files)} files in library:")
            debug_print("=" * 60)
            for file in library_files:
                debug_print(file)
            debug_print("=" * 60)
    else:
        debug_print("Skipping file processing - arduinolib0_core not available")
    
    # Call L7_cpp_spring_boot_preprocessor.py with all library directories
    # This should run regardless of HAS_ARDUINOLIB0
    if all_libs and all_libs.get('root_dirs'):
        debug_print("\n" + "=" * 80)
        debug_print("🚀 Running L7 CPP Spring Boot Preprocessor with all library directories...")
        debug_print("=" * 80)
        
        # Get the path to L7 script (in arduinolib2_core directory)
        # Determine the scripts directory
        if library_scripts_dir:
            scripts_dir = Path(library_scripts_dir)
        else:
            # Fallback: construct from library_dir
            scripts_dir = Path(library_dir) / "arduinolib2_scripts"
        
        l7_script_path = scripts_dir / "arduinolib2_core" / "L7_cpp_spring_boot_preprocessor.py"
        
        if not l7_script_path.exists():
            debug_print(f"⚠️  Warning: L7 script not found at {l7_script_path}")
            return
        
        # Build include paths: project src directory + all library directories
        include_paths = []
        
        # Add project src directory if it exists
        if project_dir:
            project_src = Path(project_dir) / "src"
            if project_src.exists():
                include_paths.append(str(project_src))
        
        # Add all library root directories (filter out arduinojson-src)
        for lib_root in all_libs['root_dirs']:
            lib_path = Path(lib_root)
            lib_name = lib_path.name.lower()
            
            # Filter out arduinojson-src and ArduinoJson directories
            if "arduinojson" in lib_name or "arduinojson-src" in lib_name:
                continue
            
            # Add the library root and its src directory if it exists
            include_paths.append(str(lib_path))
            lib_src = lib_path / "src"
            if lib_src.exists():
                include_paths.append(str(lib_src))
        
        # Build the command
        cmd = ["python", str(l7_script_path)]
        
        if include_paths:
            cmd.extend(["--include"] + include_paths)
        
        # Add dispatcher file - look in the library directory (arduinolib2) instead of client project
        dispatcher_file = Path(library_dir) / "src" / "HttpRequestDispatcher.h"
        if dispatcher_file.exists():
            cmd.extend(["--dispatcher-file", str(dispatcher_file)])
            debug_print(f"Using dispatcher file: {dispatcher_file}")
        else:
            debug_print(f"⚠️  Warning: HttpRequestDispatcher.h not found at {dispatcher_file}")
        
        debug_print(f"\nRunning: {' '.join(cmd)}")
        debug_print(f"Include paths: {include_paths}")
        
        # Run the command
        try:
            result = subprocess.run(cmd, cwd=project_dir if project_dir else os.getcwd(), 
                                  capture_output=False, text=True)
            
            if result.returncode == 0:
                debug_print("\n✅ L7 CPP Spring Boot Preprocessor completed successfully")
            else:
                debug_print(f"\n⚠️  L7 CPP Spring Boot Preprocessor exited with code {result.returncode}")
        except Exception as e:
            debug_print(f"\n❌ Error running L7 CPP Spring Boot Preprocessor: {e}")
    else:
        debug_print("\n⚠️  No library directories found, skipping L7 preprocessing")
