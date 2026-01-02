#!/usr/bin/env python3
"""
Script to check if C++ files contain the @RestController annotation above class declarations.
Validates that @RestController annotation appears before a class definition.
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set


def find_rest_controller_macros(file_path: str) -> List[Dict[str, str]]:
    """
    Find all @RestController annotations in a C++ file and their context.
    
    Args:
        file_path: Path to the C++ file (.cpp, .h, or .hpp)
        
    Returns:
        List of dictionaries with 'macro', 'line_number', 'context', 'class_name', and 'has_class' keys
    """
    rest_controller_macros = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return []
    
    # Pattern to match @RestController annotation
    # Pattern: /// @RestController or ///@RestController (ignoring whitespace)
    # Also check for already processed /* @RestController */ pattern
    rest_controller_annotation_pattern = re.compile(r'///\s*@RestController\b')
    rest_controller_processed_pattern = re.compile(r'/\*\s*@RestController\s*\*/')
    
    # Pattern to match class declarations
    # Allow for keywords like 'final', inheritance, etc. between class name and colon/brace
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:.*?[:{]|[:{])'
    
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Skip already processed annotations
        if rest_controller_processed_pattern.search(stripped_line):
            continue
        
        # Skip comments (but not the annotation itself which is in a comment)
        if stripped_line.startswith('/*'):
            continue
        # Skip other single-line comments that aren't the annotation
        if stripped_line.startswith('//') and not rest_controller_annotation_pattern.search(stripped_line):
            continue
            
        # Check if line contains valid @RestController annotation
        rest_controller_match = rest_controller_annotation_pattern.search(stripped_line)
        if rest_controller_match:
            annotation_text = rest_controller_match.group(0)
            
            # Look ahead for class declaration (within next few lines)
            # Allow other annotations/macros to appear between @RestController and class
            class_found = False
            class_name = ""
            context_lines = []
            
            # Check next 10 lines for class declaration (allowing for multiple annotations/macros)
            # Start from the line after @RestController (line_num + 1)
            for i in range(line_num + 1, min(line_num + 11, len(lines) + 1)):
                if i <= len(lines):
                    next_line = lines[i - 1].strip()
                    context_lines.append(next_line)
                    
                    # Skip comments (but not annotations)
                    if next_line.startswith('/*'):
                        continue
                    # Skip other single-line comments that aren't annotations
                    if next_line.startswith('//') and not re.search(r'///\s*@(RestController|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|NotNull|NotEmpty|NotBlank|Id|Entity|Serializable|Repository|ServerImpl)\b', next_line):
                        continue
                    
                    # Check for class declaration first
                    class_match = re.search(class_pattern, next_line)
                    if class_match:
                        class_found = True
                        class_name = class_match.group(1)
                        break
                    
                    # If empty line, continue looking
                    if not next_line:
                        continue
                    
                    # Check if it's an annotation or macro - allow REST annotations and other macros
                    # Pattern: starts with uppercase letter(s), optionally followed by parentheses, or annotation pattern
                    is_annotation_or_macro = (
                        re.search(r'///\s*@(RestController|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\b', next_line) or
                        next_line.startswith(('COMPONENT', 'SCOPE', 'VALIDATE')) or
                        re.match(r'^[A-Z][A-Za-z0-9_]*\s*(?:\(|$)', next_line)
                    )
                    
                    # If it's not an annotation/macro and not a class, stop looking
                    if not is_annotation_or_macro:
                        break
            
            rest_controller_macros.append({
                'macro': annotation_text,
                'line_number': line_num,
                'context': context_lines,
                'class_name': class_name,
                'has_class': class_found
            })
    
    return rest_controller_macros


def check_rest_controller_macro_exists(file_path: str) -> bool:
    """
    Simple check if @RestController annotation exists in the file.
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        True if active @RestController annotation is found above a class, False otherwise
    """
    rest_controller_macros = find_rest_controller_macros(file_path)
    
    # Check if any RestController macro has a class following it
    for macro_info in rest_controller_macros:
        if macro_info['has_class']:
            return True
    
    return False


def validate_rest_controller_macro_placement(file_path: str) -> Dict[str, any]:
    """
    Comprehensive validation of @RestController annotation placement and usage.
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        Dictionary with validation results
    """
    rest_controller_macros = find_rest_controller_macros(file_path)
    
    if not rest_controller_macros:
        return {
            'file_path': file_path,
            'has_rest_controller': False,
            'rest_controller_count': 0,
            'valid_placements': 0,
            'invalid_placements': 0,
            'issues': ['No @RestController annotation found']
        }
    
    valid_placements = 0
    invalid_placements = 0
    issues = []
    
    for macro_info in rest_controller_macros:
        if macro_info['has_class']:
            valid_placements += 1
        else:
            invalid_placements += 1
            issues.append(f"@RestController annotation at line {macro_info['line_number']} not followed by class declaration")
    
    return {
        'file_path': file_path,
        'has_rest_controller': True,
        'rest_controller_count': len(rest_controller_macros),
        'valid_placements': valid_placements,
        'invalid_placements': invalid_placements,
        'issues': issues,
        'macros': rest_controller_macros
    }


def check_multiple_files(file_paths: List[str]) -> Dict[str, Dict[str, any]]:
    """
    Check RestController macro requirements in multiple files.
    
    Args:
        file_paths: List of file paths to check
        
    Returns:
        Dictionary mapping file paths to validation results
    """
    results = {}
    
    for file_path in file_paths:
        results[file_path] = validate_rest_controller_macro_placement(file_path)
    
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


def main():
    """Main function to handle command line arguments and execute the validation."""
    parser = argparse.ArgumentParser(
        description="Check if C++ files contain @RestController annotation above class declarations"
    )
    parser.add_argument(
        "files", 
        nargs="+", 
        help="C++ source files to analyze (.cpp, .h, .hpp, etc.)"
    )
    parser.add_argument(
        "--simple", 
        action="store_true",
        help="Simple check: just show if RestController exists or not"
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
            has_rest_controller = check_rest_controller_macro_exists(file_path)
            results[file_path] = {'has_rest_controller': has_rest_controller}
            
            status = "✓ @RestController found" if has_rest_controller else "✗ No @RestController"
            print(f"{file_path}: {status}")
    else:
        # Detailed validation mode
        results = check_multiple_files(valid_files)
        
        # Display results
        for file_path, result in results.items():
            print(f"\n{'='*60}")
            print(f"File: {file_path}")
            print(f"{'='*60}")
            
            if result['has_rest_controller']:
                print(f"✓ @RestController annotation found ({result['rest_controller_count']} occurrences)")
                print(f"  Valid placements: {result['valid_placements']}")
                print(f"  Invalid placements: {result['invalid_placements']}")
                
                if result['valid_placements'] > 0:
                    print(f"  Status: ✓ @RestController annotation is properly placed above class")
                else:
                    print(f"  Status: ✗ @RestController annotation found but not followed by class")
                
                if args.detailed and result['macros']:
                    print(f"\n  Detailed annotation information:")
                    for macro in result['macros']:
                        print(f"    Line {macro['line_number']}: {macro['macro']}")
                        if macro['has_class']:
                            print(f"      → Class: {macro['class_name']}")
                        else:
                            print(f"      → No class found")
                
                if result['issues']:
                    print(f"\n  Issues found:")
                    for issue in result['issues']:
                        print(f"    ⚠ {issue}")
            else:
                print("✗ No @RestController annotation found")
    
    # Show summary if requested
    if args.summary and not args.simple:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        total_files = len(valid_files)
        files_with_rest_controller = len([r for r in results.values() if r['has_rest_controller']])
        total_rest_controllers = sum([r.get('rest_controller_count', 0) for r in results.values()])
        total_valid_placements = sum([r.get('valid_placements', 0) for r in results.values()])
        total_invalid_placements = sum([r.get('invalid_placements', 0) for r in results.values()])
        
        print(f"Files analyzed: {total_files}")
        print(f"Files with @RestController: {files_with_rest_controller}")
        print(f"Files without @RestController: {total_files - files_with_rest_controller}")
        print(f"Total @RestController annotations: {total_rest_controllers}")
        print(f"Valid placements: {total_valid_placements}")
        print(f"Invalid placements: {total_invalid_placements}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            if args.simple:
                for file_path, result in results.items():
                    status = "@RestController found" if result['has_rest_controller'] else "No @RestController"
                    f.write(f"{file_path}: {status}\n")
            else:
                for file_path, result in results.items():
                    f.write(f"{file_path}:\n")
                    if result['has_rest_controller']:
                        f.write(f"  @RestController annotations: {result['rest_controller_count']}\n")
                        f.write(f"  Valid placements: {result['valid_placements']}\n")
                        f.write(f"  Invalid placements: {result['invalid_placements']}\n")
                        if result['issues']:
                            f.write(f"  Issues: {', '.join(result['issues'])}\n")
                    else:
                        f.write(f"  No @RestController annotation found\n")
                    f.write("\n")
        print(f"\nResults saved to: {args.output}")
    
    return results


# Export functions for other scripts to import
__all__ = [
    'find_rest_controller_macros',
    'check_rest_controller_macro_exists',
    'validate_rest_controller_macro_placement',
    'check_multiple_files',
    'main'
]


if __name__ == "__main__":
    # When run as script, execute main and store result
    result = main()
