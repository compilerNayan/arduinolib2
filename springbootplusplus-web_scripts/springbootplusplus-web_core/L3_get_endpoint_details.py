#!/usr/bin/env python3
"""
Script to extract endpoint details from HTTP mapping annotations inside C++ controller classes.
Finds @GetMapping, @PostMapping, @PutMapping, @DeleteMapping, and @PatchMapping annotations above functions 
inside the class, extracts function details, and combines with base URL to form complete endpoint URLs.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any


def find_class_and_interface(file_path: str) -> Optional[Dict[str, str]]:
    """
    Find class name and interface name from class declaration.
    Handles both 'class Xyz : public Interface' and 'class Xyz final : public Interface'.
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        Dictionary with 'class_name' and 'interface_name', or None if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        # print(f"Error: File '{file_path}' not found")
        return None
    except Exception as e:
        # print(f"Error reading file '{file_path}': {e}")
        return None
    
    # Pattern to match class declarations with inheritance
    # Matches: class Xyz : public Interface or class Xyz final : public Interface
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:final\s*)?:\s*public\s+([A-Za-z_][A-Za-z0-9_]*)'
    
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Skip commented lines
        if stripped_line.startswith('//') or stripped_line.startswith('/*') or stripped_line.startswith('*'):
            continue
        
        # Check for class declaration with inheritance
        match = re.search(class_pattern, stripped_line)
        if match:
            class_name = match.group(1)
            interface_name = match.group(2)
            return {
                'class_name': class_name,
                'interface_name': interface_name,
                'line_number': line_num
            }
    
    return None


def find_class_boundaries(file_path: str) -> Optional[Tuple[int, int]]:
    """
    Find the start and end line numbers of the class definition.
    
    Args:
        file_path: Path to the C++ file
        
    Returns:
        Tuple of (start_line, end_line) or None if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        # print(f"Error reading file '{file_path}': {e}")
        return None
    
    class_start = None
    brace_count = 0
    
    # Pattern to match class declaration
    class_pattern = r'class\s+[A-Za-z_][A-Za-z0-9_]*\s*(?:.*?[:{]|[:{])'
    
    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        
        # Allow annotations (/// @...) to be present before the class, but skip other comments
        if stripped_line.startswith('/*'):
            continue
        if stripped_line.startswith('//') and not re.search(r'///\s*@\w+\b', stripped_line):
            continue
        
        # Check if this is the class declaration line
        if class_start is None:
            if re.search(class_pattern, stripped_line):
                class_start = line_num
                # Count opening brace on the same line
                brace_count += stripped_line.count('{')
                if brace_count > 0:
                    continue
        
        # If we're inside the class, count braces
        if class_start is not None:
            brace_count += stripped_line.count('{')
            brace_count -= stripped_line.count('}')
            
            # If braces are balanced and we've closed the class, we're done
            if brace_count == 0:
                return (class_start, line_num)
    
    return None


def parse_function_signature(line: str) -> Optional[Dict[str, str]]:
    """
    Parse a function signature to extract return type, function name, and first argument type.
    
    Args:
        line: Function signature line (e.g., "MyReturnDto myEndpoint(MyInputDto dto)")
        
    Returns:
        Dictionary with 'return_type', 'function_name', 'first_arg_type', or None if parsing fails
    """
    # Pattern to match function signature
    # Matches: ReturnType functionName(Type1 arg1, Type2 arg2, ...)
    # Handles optional override, const, etc.
    function_pattern = r'([A-Za-z_][A-Za-z0-9_<>*&:,\s]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)'
    
    match = re.search(function_pattern, line.strip())
    if not match:
        return None
    
    return_type = match.group(1).strip()
    function_name = match.group(2).strip()
    args_str = match.group(3).strip()
    
    # Extract first argument type
    first_arg_type = None
    if args_str:
        # Split by comma, but be careful with template types
        # Simple approach: take everything before the first comma or space after the type
        first_arg_match = re.match(r'([A-Za-z_][A-Za-z0-9_<>*&:,\s]*?)(?:\s+[A-Za-z_][A-Za-z0-9_]*)?(?:\s*,|\s*$)', args_str)
        if first_arg_match:
            first_arg_type = first_arg_match.group(1).strip()
        else:
            # If no match, try to extract the first word as type
            parts = args_str.split()
            if parts:
                first_arg_type = parts[0]
    
    return {
        'return_type': return_type,
        'function_name': function_name,
        'first_arg_type': first_arg_type or ""
    }


def find_mapping_endpoints(file_path: str, base_url: str, class_name: str, interface_name: str) -> List[Dict[str, Any]]:
    """
    Find all HTTP mapping endpoints (GetMapping, PostMapping, PutMapping, DeleteMapping, PatchMapping) 
    inside the class and extract their details.
    
    Args:
        file_path: Path to the C++ file
        base_url: Base URL to concatenate with mapping paths
        class_name: Name of the class
        interface_name: Name of the interface
        
    Returns:
        List of dictionaries with endpoint details
    """
    print(f"[DEBUG] find_mapping_endpoints: file={file_path}, base_url={base_url}, class={class_name}, interface={interface_name}", file=sys.stderr)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"[DEBUG] Error reading file '{file_path}': {e}", file=sys.stderr)
        return []
    
    # Find class boundaries
    boundaries = find_class_boundaries(file_path)
    if not boundaries:
        print(f"[DEBUG] No class boundaries found in {file_path}", file=sys.stderr)
        return []
    
    class_start, class_end = boundaries
    print(f"[DEBUG] Class boundaries: start={class_start}, end={class_end}", file=sys.stderr)
    
    endpoints = []
    
    # Pattern to match any HTTP mapping annotation: /// @GetMapping("/path"), /// @PostMapping("/path"), etc.
    # Also check for already processed /* @GetMapping("/path") */ pattern
    # Note: [^"\']* allows empty strings (zero or more characters), not [^"\']+ (one or more)
    mapping_annotation_pattern = re.compile(r'///\s*@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*\(\s*["\']([^"\']*)["\']\s*\)')
    mapping_processed_pattern = re.compile(r'/\*\s*@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*\(\s*["\'][^"\']*["\']\s*\)\s*\*/')
    
    # Pattern to match legacy HTTP mapping macros (for backward compatibility)
    mapping_macro_pattern = re.compile(r'(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*\(\s*["\']([^"\']*)["\']\s*\)')
    
    # Pattern to match function signature
    function_pattern = r'([A-Za-z_][A-Za-z0-9_<>*&:,\s]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)'
    
    # Scan inside the class (between class_start and class_end)
    i = class_start
    while i < class_end:
        line = lines[i - 1].strip()  # Convert to 0-indexed
        
        # Skip already processed annotations
        if mapping_processed_pattern.search(line):
            i += 1
            continue
        
        # Skip comments (but not annotations)
        if line.startswith('/*'):
            i += 1
            continue
        # Skip other single-line comments that aren't annotations
        if line.startswith('//') and not mapping_annotation_pattern.search(line):
            i += 1
            continue
        
        # Check for HTTP mapping annotation first (/// @GetMapping("/path"))
        mapping_match = mapping_annotation_pattern.search(line)
        if mapping_match:
            http_method_annotation = mapping_match.group(1)  # e.g., "GetMapping", "PostMapping", etc.
            mapping_path = mapping_match.group(2)
            print(f"[DEBUG] Found annotation match: method={http_method_annotation}, path='{mapping_path}' (line {i})", file=sys.stderr)
        else:
            # Fallback: check for legacy mapping macro (for backward compatibility)
            mapping_match = mapping_macro_pattern.search(line)
            if mapping_match:
                http_method_annotation = mapping_match.group(1)
                mapping_path = mapping_match.group(2)
                print(f"[DEBUG] Found macro match: method={http_method_annotation}, path='{mapping_path}' (line {i})", file=sys.stderr)
            else:
                i += 1
                continue
        
        # Extract HTTP method from annotation/macro name (GetMapping -> GET, PostMapping -> POST, etc.)
        http_method = http_method_annotation.replace('Mapping', '').upper()
        print(f"[DEBUG] HTTP method: {http_method}, mapping_path: '{mapping_path}'", file=sys.stderr)
        
        # Construct full endpoint URL
        # Ensure proper URL concatenation: base_url + mapping_path
        # Handle empty mapping_path (maps to base_url only)
        base_url_clean = base_url.rstrip('/')
        if not mapping_path:  # Empty string
            endpoint_url = base_url_clean
            print(f"[DEBUG] Empty mapping_path, using base_url only: '{endpoint_url}'", file=sys.stderr)
        else:
            # mapping_path is not empty
            if not mapping_path.startswith('/'):
                mapping_path = '/' + mapping_path
            endpoint_url = base_url_clean + mapping_path
            print(f"[DEBUG] Non-empty mapping_path, concatenated: '{endpoint_url}'", file=sys.stderr)
        
        # Look ahead for function signature (within next few lines)
        function_found = False
        function_details = None
        print(f"[DEBUG] Looking for function signature after line {i}...", file=sys.stderr)
        
        for j in range(i + 1, min(i + 5, class_end + 1)):
            if j > len(lines):
                break
            
            next_line = lines[j - 1].strip()
            
            # Skip already processed annotations
            if mapping_processed_pattern.search(next_line):
                continue
            
            # Skip already processed annotations
            if mapping_processed_pattern.search(next_line):
                continue
            
            # Skip comments (but not annotations)
            if next_line.startswith('/*'):
                continue
            # Skip other single-line comments that aren't annotations
            if next_line.startswith('//') and not mapping_annotation_pattern.search(next_line):
                continue
            
            # Skip empty lines
            if not next_line:
                continue
            
            # Check if this is a function signature
            func_details = parse_function_signature(next_line)
            if func_details:
                print(f"[DEBUG] Found function signature at line {j}: {next_line}", file=sys.stderr)
                print(f"[DEBUG] Function details: name={func_details['function_name']}, return_type={func_details['return_type']}, first_arg={func_details['first_arg_type']}", file=sys.stderr)
                function_found = True
                function_details = func_details
                break
            else:
                print(f"[DEBUG] Line {j} is not a function signature: '{next_line[:50]}...'", file=sys.stderr)
        
        if function_found and function_details:
                endpoint_info = {
                    'endpoint_url': endpoint_url,
                    'http_method': http_method,
                    'mapping_annotation': http_method_annotation,
                    'mapping_path': mapping_path,
                    'function_name': function_details['function_name'],
                    'return_type': function_details['return_type'],
                    'first_arg_type': function_details['first_arg_type'],
                    'class_name': class_name,
                    'interface_name': interface_name,
                    'mapping_line': i,
                    'function_line': j if function_found else None
                }
                print(f"[DEBUG] Adding endpoint: {http_method} {endpoint_url} -> {function_details['function_name']}", file=sys.stderr)
                endpoints.append(endpoint_info)
        else:
            print(f"[DEBUG] WARNING: No function found for {http_method} mapping at line {i}, path='{mapping_path}'", file=sys.stderr)
        
        i += 1
    
    return endpoints


def get_endpoint_details(file_path: str, base_url: str) -> Dict[str, Any]:
    """
    Get all endpoint details from a C++ controller file.
    
    Args:
        file_path: Path to the C++ file
        base_url: Base URL to concatenate with GetMapping paths
        
    Returns:
        Dictionary with class info and endpoint details
    """
    # Step 1: Get class name and interface name
    class_info = find_class_and_interface(file_path)
    if not class_info:
        return {
            'success': False,
            'error': 'Could not find class and interface declaration',
            'endpoints': []
        }
    
    class_name = class_info['class_name']
    interface_name = class_info['interface_name']
    
    # Step 2: Find all HTTP mapping endpoints inside the class
    endpoints = find_mapping_endpoints(file_path, base_url, class_name, interface_name)
    
    return {
        'success': True,
        'class_name': class_name,
        'interface_name': interface_name,
        'base_url': base_url,
        'endpoints': endpoints
    }


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


def display_endpoint_details(result: Dict[str, Any]) -> None:
    """
    Display endpoint details in a formatted way.
    
    Args:
        result: Dictionary with endpoint details
    """
    if not result['success']:
        # print(f"Error: {result.get('error', 'Unknown error')}")
        return
    
    # print(f"\n{'='*70}")
    # print(f"Class: {result['class_name']}")
    # print(f"Interface: {result['interface_name']}")
    # print(f"Base URL: {result['base_url']}")
    # print(f"{'='*70}")
    
    if not result['endpoints']:
        # print("\nNo HTTP mapping endpoints found inside the class.")
        return
    
    # print(f"\nFound {len(result['endpoints'])} endpoint(s):\n")
    
    # for idx, endpoint in enumerate(result['endpoints'], 1):
    #     print(f"Endpoint {idx}:")
    #     print(f"  HTTP Method: {endpoint['http_method']}")
    #     print(f"  URL: {endpoint['endpoint_url']}")
    #     print(f"  Mapping Annotation: {endpoint.get('mapping_annotation', endpoint.get('mapping_macro', 'N/A'))}")
    #     print(f"  Mapping Path: {endpoint['mapping_path']}")
    #     print(f"  Function Name: {endpoint['function_name']}")
    #     print(f"  Return Type: {endpoint['return_type']}")
    #     print(f"  First Argument Type: {endpoint['first_arg_type'] if endpoint['first_arg_type'] else '(none)'}")
    #     print(f"  Class Name: {endpoint['class_name']}")
    #     print(f"  Interface Name: {endpoint['interface_name']}")
    #     if endpoint.get('mapping_line'):
    #         print(f"  Mapping at line: {endpoint['mapping_line']}")
    #     if endpoint.get('function_line'):
    #         print(f"  Function at line: {endpoint['function_line']}")
    #     print()


def main():
    """Main function to handle command line arguments and execute the endpoint extraction."""
    parser = argparse.ArgumentParser(
        description="Extract endpoint details from HTTP mapping macros (GetMapping, PostMapping, PutMapping, DeleteMapping, PatchMapping) inside C++ controller classes"
    )
    parser.add_argument(
        "file",
        help="C++ source file to analyze (.cpp, .h, .hpp, etc.)"
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL to concatenate with mapping paths (e.g., '/myUrl')"
    )
    
    args = parser.parse_args()
    
    # Validate file
    if not validate_cpp_file(args.file):
        # print(f"Error: '{args.file}' is not a valid C++ file")
        return None
    
    # Get endpoint details
    result = get_endpoint_details(args.file, args.base_url)
    
    # Display results
    display_endpoint_details(result)
    
    return result


# Export functions for other scripts to import
__all__ = [
    'find_class_and_interface',
    'find_class_boundaries',
    'parse_function_signature',
    'find_mapping_endpoints',
    'get_endpoint_details',
    'display_endpoint_details',
    'main'
]


if __name__ == "__main__":
    # When run as script, execute main and store result
    result = main()
