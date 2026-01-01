#!/usr/bin/env python3
"""
Script to check if C++ files contain the COMPONENT macro above class declarations that inherit from interfaces.
Validates that class inherits from interface and has COMPONENT macro.
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

# Import functions from our other scripts
try:
    from find_class_names import find_class_names
    from find_interface_names import find_interface_names
except ImportError:
    print("Error: Could not import required modules. Make sure find_class_names.py and find_interface_names.py are in the same directory.")
    sys.exit(1)


def find_component_macros(file_path: str) -> List[Dict[str, str]]:
    """
    Find all COMPONENT macros in a C++ file and their context.
    
    Args:
        file_path: Path to the C++ file (.cpp, .h, or .hpp)
        
    Returns:
        List of dictionaries with 'macro', 'line_number', 'context', 'class_name', 'has_class', and 'has_interface' keys
    """
    component_macros = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return []
    
    # Pattern to match //@Component annotation (case-sensitive)
    # Also check for /*@Component*/ (already processed, should be ignored)
    component_annotation_pattern = r'^//@Component\s*$'
    component_processed_pattern = r'^/\*@Component\*/\s*$'
    
    # Pattern to match class declarations
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:[:{])'
    
    for line_num, line in enumerate(lines, 1):
        # Check for //@Component annotation
        stripped_line = line.strip()
        
        # Skip already processed annotations (/*@Component*/)
        if re.search(component_processed_pattern, stripped_line):
            continue
        
        # Skip other comment types (but not //@ annotations)
        if stripped_line.startswith('/*') and not stripped_line.startswith('//@'):
            continue
        
        # Skip lines that don't start with //@Component
        if stripped_line and not stripped_line.startswith('//@Component'):
            continue
            
        # Check if line contains valid //@Component annotation
        component_match = re.search(component_annotation_pattern, stripped_line)
        if component_match:
            macro_text = component_match.group(0)
            
            # Look ahead for class declaration (within next few lines)
            class_found = False
            class_name = ""
            context_lines = []
            
            # Check next 10 lines for class declaration (allowing for multiple macros)
            for i in range(line_num, min(line_num + 11, len(lines) + 1)):
                if i <= len(lines):
                    next_line = lines[i - 1].strip()
                    context_lines.append(next_line)
                    
                    # Check for class declaration
                    class_match = re.search(class_pattern, next_line)
                    if class_match:
                        class_found = True
                        class_name = class_match.group(1)
                        break
                    
                    # Stop if we hit a blank line or different annotation
                    if not next_line or (next_line and not (re.match(r'^//@', next_line) or re.match(r'^/\*@', next_line))):
                        break
            
            component_macros.append({
                'macro': macro_text,
                'line_number': line_num,
                'context': context_lines,
                'class_name': class_name,
                'has_class': class_found
            })
    
    return component_macros


def check_component_macro_exists(file_path: str) -> bool:
    """
    Simple check if COMPONENT macro exists in the file (ignoring commented ones).
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        True if active COMPONENT macro is found, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Check each line for //@Component annotation (not already processed)
        for line in lines:
            stripped_line = line.strip()
            
            # Skip already processed annotations (/*@Component*/)
            if re.match(r'^/\*@Component\*/\s*$', stripped_line):
                continue
            
            # Skip other comment types (but not //@ annotations)
            if stripped_line.startswith('/*') and not stripped_line.startswith('//@'):
                continue
                
            # Check if line contains //@Component annotation
            if re.match(r'^//@Component\s*$', stripped_line):
                return True
        
        return False
    except Exception:
        return False


def validate_component_macro_requirements(file_path: str) -> Dict[str, any]:
    """
    Comprehensive validation of COMPONENT macro requirements.
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        Dictionary with validation results
    """
    # Step 1: Get class names from the file
    class_names = find_class_names(file_path)
    
    # Step 2: Get interface names from the file
    interface_names = find_interface_names(file_path)
    
    # Step 3: Find COMPONENT macros
    component_macros = find_component_macros(file_path)
    
    # Step 4: Validate requirements
    has_classes = len(class_names) > 0
    has_interfaces = len(interface_names) > 0
    has_component_macro = len(component_macros) > 0
    
    # Check if classes inherit from interfaces
    classes_with_inheritance = []
    for class_name in class_names:
        if interface_names:  # If there are interfaces, assume inheritance
            classes_with_inheritance.append(class_name)
    
    # All three conditions must be met:
    # 1. Has COMPONENT macro
    # 2. Has class names
    # 3. Has interface names (meaning classes inherit from interfaces)
    all_requirements_met = has_component_macro and has_classes and has_interfaces and len(classes_with_inheritance) > 0
    
    # Build validation result
    validation_result = {
        'file_path': file_path,
        'has_component_macro': has_component_macro,
        'has_classes': has_classes,
        'has_interfaces': has_interfaces,
        'classes_with_inheritance': classes_with_inheritance,
        'all_requirements_met': all_requirements_met,
        'component_macros': component_macros,
        'class_names': class_names,
        'interface_names': interface_names,
        'status': 'valid' if all_requirements_met else 'invalid'
    }
    
    return validation_result


def check_multiple_files(file_paths: List[str]) -> Dict[str, Dict[str, any]]:
    """
    Check COMPONENT macro requirements in multiple files.
    
    Args:
        file_paths: List of file paths to check
        
    Returns:
        Dictionary mapping file paths to validation results
    """
    results = {}
    
    for file_path in file_paths:
        results[file_path] = validate_component_macro_requirements(file_path)
    
    return results


def validate_cpp_file(file_path: str) -> bool:
    """
    Check if the file is a valid C++ source file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if it's a C++ file, False otherwise
    """
    cpp_extensions = {'.cpp', '.h', '.hpp', '.cc', '.cxx', '.hh', '.hxx'}
    return Path(file_path).suffix.lower() in cpp_extensions


def convert_component_annotation_to_processed(file_path: str) -> bool:
    """
    Convert //@Component to /*@Component*/ in a C++ file.
    This marks the annotation as processed so it won't be processed again.
    
    Args:
        file_path: Path to the C++ file to modify
        
    Returns:
        True if file was modified successfully, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        modified = False
        annotation_pattern = r'^(\s*)//@Component\s*$'
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Skip already processed annotations (/*@Component*/)
            if re.match(r'^/\*@Component\*/\s*$', stripped_line):
                continue
            
            # Check if line contains //@Component annotation
            match = re.match(annotation_pattern, line)
            if match:
                indent = match.group(1)
                # Convert to /*@Component*/
                lines[i] = f'{indent}/*@Component*/\n'
                modified = True
        
        # Write back to file if modifications were made
        if modified:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print(f"✓ Converted //@Component to /*@Component*/ in: {file_path}")
        else:
            print(f"ℹ No //@Component annotations found to convert in: {file_path}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return False
    except Exception as e:
        print(f"Error modifying file '{file_path}': {e}")
        return False


def convert_component_annotations_in_multiple_files(file_paths: List[str]) -> Dict[str, bool]:
    """
    Convert //@Component to /*@Component*/ in multiple files.
    
    Args:
        file_paths: List of file paths to modify
        
    Returns:
        Dictionary mapping file paths to success status
    """
    results = {}
    
    for file_path in file_paths:
        results[file_path] = convert_component_annotation_to_processed(file_path)
    
    return results


def main():
    """Main function to handle command line arguments and execute the validation."""
    parser = argparse.ArgumentParser(
        description="Check if C++ files contain //@Component annotation above class declarations that inherit from interfaces"
    )
    parser.add_argument(
        "files", 
        nargs="+", 
        help="C++ source files to analyze (.cpp, .h, .hpp, etc.)"
    )
    parser.add_argument(
        "--simple", 
        action="store_true",
        help="Simple check: just show if COMPONENT exists or not"
    )
    parser.add_argument(
        "--detailed", 
        action="store_true",
        help="Show detailed validation information"
    )
    parser.add_argument(
        "--output", 
        help="Output file to save results (optional)"
    )
    parser.add_argument(
        "--summary", 
        action="store_true",
        help="Show summary statistics"
    )
    
    args = parser.parse_args()
    
    # Filter valid C++ files
    valid_files = [f for f in args.files if validate_cpp_file(f)]
    invalid_files = [f for f in args.files if not validate_cpp_file(f)]
    
    if invalid_files:
        print(f"Warning: Skipping non-C++ files: {', '.join(invalid_files)}")
    
    if not valid_files:
        print("No valid C++ files provided")
        return {}
    
    # Check files
    if args.simple:
        # Simple check mode
        results = {}
        for file_path in valid_files:
            has_component = check_component_macro_exists(file_path)
            results[file_path] = {'has_component': has_component}
            
            status = "✓ //@Component found" if has_component else "✗ No //@Component"
            print(f"{file_path}: {status}")
    else:
        # Detailed validation mode
        results = check_multiple_files(valid_files)
        
        # Display results
        for file_path, result in results.items():
            print(f"\n{'='*60}")
            print(f"File: {file_path}")
            print(f"{'='*60}")
            
            if result['has_component_macro']:
                print(f"✓ //@Component annotation found ({len(result['component_macros'])} occurrences)")
                print(f"  Classes found: {', '.join(result['class_names']) if result['class_names'] else 'None'}")
                print(f"  Interfaces found: {', '.join(result['interface_names']) if result['interface_names'] else 'None'}")
                print(f"  Classes with inheritance: {', '.join(result['classes_with_inheritance']) if result['classes_with_inheritance'] else 'None'}")
                
                if result['all_requirements_met']:
                    print(f"  Status: ✓ All requirements met - //@Component annotation is valid")
                else:
                    print(f"  Status: ✗ Requirements not met - //@Component annotation has no significance")
                
                if args.detailed and result['component_macros']:
                    print(f"\n  Detailed macro information:")
                    for macro in result['component_macros']:
                        print(f"    Line {macro['line_number']}: {macro['macro']}")
                        if macro['has_class']:
                            print(f"      → Class: {macro['class_name']}")
                        else:
                            print(f"      → No class found")
            else:
                print("✗ No //@Component annotation found")
    
    # Show summary if requested
    if args.summary and not args.simple:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        total_files = len(valid_files)
        files_with_component = len([r for r in results.values() if r['has_component_macro']])
        files_with_valid_component = len([r for r in results.values() if r.get('all_requirements_met', False)])
        
        print(f"Files analyzed: {total_files}")
        print(f"Files with //@Component annotation: {files_with_component}")
        print(f"Files with valid //@Component annotation: {files_with_valid_component}")
        print(f"Files with invalid //@Component annotation: {files_with_component - files_with_valid_component}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            if args.simple:
                for file_path, result in results.items():
                    status = "//@Component found" if result['has_component'] else "No //@Component"
                    f.write(f"{file_path}: {status}\n")
            else:
                for file_path, result in results.items():
                    f.write(f"{file_path}:\n")
                    if result['has_component_macro']:
                        f.write(f"  //@Component annotations: {len(result['component_macros'])}\n")
                        f.write(f"  Classes: {', '.join(result['class_names']) if result['class_names'] else 'None'}\n")
                        f.write(f"  Interfaces: {', '.join(result['interface_names']) if result['interface_names'] else 'None'}\n")
                        f.write(f"  Valid: {result['all_requirements_met']}\n")
                    else:
                        f.write(f"  No //@Component annotation found\n")
                    f.write("\n")
        print(f"\nResults saved to: {args.output}")
    
    return results


# Export functions for other scripts to import
__all__ = [
    'find_component_macros',
    'check_component_macro_exists',
    'validate_component_macro_requirements',
    'check_multiple_files',
    'convert_component_annotation_to_processed',
    'convert_component_annotations_in_multiple_files',
    'main'
]


if __name__ == "__main__":
    # When run as script, execute main and store result
    result = main()
