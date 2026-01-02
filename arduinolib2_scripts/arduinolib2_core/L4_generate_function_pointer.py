#!/usr/bin/env python3
"""
Script to generate function pointer code for HTTP mapping endpoints.
Takes endpoint details as command-line parameters and generates the appropriate
function pointer template based on the HTTP method (GET, POST, PUT, DELETE, PATCH).
"""

import argparse
from typing import Dict, Optional


def get_mapping_variable_name(http_method: str) -> str:
    """
    Get the mapping variable name based on HTTP method.
    
    Args:
        http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        
    Returns:
        Mapping variable name (e.g., "getMappings", "postMappings", etc.)
    """
    method_lower = http_method.lower()
    return f"{method_lower}Mappings"


def generate_function_pointer(
    url: str,
    http_method: str,
    function_name: str,
    return_type: str,
    first_arg_type: str,
    interface_name: str
) -> str:
    """
    Generate function pointer code for an HTTP mapping endpoint.
    
    Args:
        url: Endpoint URL as string (e.g., "/myUrl/mysomeget")
        http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        function_name: Function name (e.g., "myFun")
        return_type: Return type (e.g., "int", "MyReturnDto")
        first_arg_type: First argument type (e.g., "TestDto", "MyInputDto")
        interface_name: Interface name (e.g., "ITestController")
        
    Returns:
        Generated function pointer code as string
    """
    # Get the mapping variable name based on HTTP method
    mapping_var = get_mapping_variable_name(http_method)
    
    # Generate the function pointer code
    code = f"{mapping_var}[\"{url}\"] = [](CStdString arg) -> StdString {{\n"
    code += "    AUTOWIRED\n"
    code += f"    {interface_name}Ptr controller;\n"
    
    # Handle case where there's no argument (first_arg_type is empty or "none")
    if first_arg_type and first_arg_type.lower() not in ["", "none", "(none)"]:
        code += f"    Val returnValue = controller->{function_name}(nayan::serializer::SerializationUtility::Deserialize<{first_arg_type}>(arg));\n"
    else:
        code += f"    Val returnValue = controller->{function_name}();\n"
    
    code += "    return nayan::serializer::SerializationUtility::Serialize(returnValue);\n"
    code += "};"
    
    return code


def main():
    """Main function to handle command line arguments and generate function pointer code."""
    parser = argparse.ArgumentParser(
        description="Generate function pointer code for HTTP mapping endpoints"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Endpoint URL as string (e.g., '/myUrl/mysomeget')"
    )
    parser.add_argument(
        "--http-method",
        required=True,
        choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
        help="HTTP method (GET, POST, PUT, DELETE, PATCH)"
    )
    parser.add_argument(
        "--function-name",
        required=True,
        help="Function name (e.g., 'myFun')"
    )
    parser.add_argument(
        "--return-type",
        required=True,
        help="Return type (e.g., 'int', 'MyReturnDto')"
    )
    parser.add_argument(
        "--first-arg-type",
        default="",
        help="First argument type (e.g., 'TestDto', 'MyInputDto'). Leave empty if no arguments."
    )
    parser.add_argument(
        "--interface-name",
        required=True,
        help="Interface name (e.g., 'ITestController')"
    )
    parser.add_argument(
        "--output",
        help="Output file to save the generated code (optional). If not provided, prints to stdout."
    )
    
    args = parser.parse_args()
    
    # Generate the function pointer code
    generated_code = generate_function_pointer(
        url=args.url,
        http_method=args.http_method,
        function_name=args.function_name,
        return_type=args.return_type,
        first_arg_type=args.first_arg_type,
        interface_name=args.interface_name
    )
    
    # Output the generated code
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(generated_code)
                f.write('\n')
            print(f"Generated code saved to: {args.output}")
        except Exception as e:
            print(f"Error writing to file '{args.output}': {e}")
            print("\nGenerated code:")
            print(generated_code)
    else:
        print(generated_code)
    
    return generated_code


# Export functions for other scripts to import
__all__ = [
    'get_mapping_variable_name',
    'generate_function_pointer',
    'main'
]


if __name__ == "__main__":
    # When run as script, execute main and store result
    result = main()
