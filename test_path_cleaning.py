#!/usr/bin/env python3
"""Test the path cleaning functionality."""

from pathlib import Path

def clean_file_path(file_path: str) -> str:
    """Clean up file paths that may have extra quotes or brackets."""
    # Remove surrounding brackets, quotes (both straight and curly)
    cleaned = file_path.strip()
    cleaned = cleaned.strip("[]")
    cleaned = cleaned.strip("'\"''""")
    cleaned = cleaned.strip()
    return cleaned

# Test cases with various malformed paths
test_paths = [
    # Normal path
    "/Users/miguelbravo/Downloads/meeting-transcript.txt",
    
    # Path with curly quotes (as seen in the error)
    "['/Users/miguelbravo/Downloads/meeting-transcript.txt']",
    
    # Path with straight quotes
    "'/Users/miguelbravo/Downloads/file.txt'",
    '"/Users/miguelbravo/Downloads/file.txt"',
    
    # Path with curly quotes
    "'/Users/miguelbravo/Downloads/file.txt'",
    # Skip the double curly quotes test - causes syntax error
    
    # Path with brackets
    "[/Users/miguelbravo/Downloads/file.txt]",
    
    # Path with both brackets and quotes
    '["test_file.txt"]',
    "['test_file.txt']",
    
    # Path with extra whitespace
    "  /Users/miguelbravo/Downloads/file.txt  ",
    " ['/Users/miguelbravo/Downloads/file.txt'] ",
    
    # Complex case with multiple issues
    " ['/Users/miguelbravo/Downloads/meeting-transcript.txt'] ",
]

print("Testing path cleaning function:\n")
print("-" * 80)

for original in test_paths:
    cleaned = clean_file_path(original)
    print(f"Original: {repr(original)}")
    print(f"Cleaned:  {repr(cleaned)}")
    print(f"Filename: {Path(cleaned).name}")
    print("-" * 80)

# Test matching logic
print("\n\nTesting matching logic:")
print("=" * 80)

# Simulate the attached_files list with malformed path
attached_files = ["['/Users/miguelbravo/Downloads/meeting-transcript.txt']"]

# Test various input formats
test_inputs = [
    "meeting-transcript.txt",  # Just filename
    "/Users/miguelbravo/Downloads/meeting-transcript.txt",  # Full path
    "'/Users/miguelbravo/Downloads/meeting-transcript.txt'",  # With quotes
    "['/Users/miguelbravo/Downloads/meeting-transcript.txt']",  # Exact match to malformed
]

for file_name in test_inputs:
    print(f"\nInput: {repr(file_name)}")
    
    # Clean the input
    cleaned_input = clean_file_path(file_name)
    file_name_only = Path(cleaned_input).name
    print(f"Cleaned input: {repr(cleaned_input)}")
    print(f"Filename only: {repr(file_name_only)}")
    
    # Try to find match
    matching_file = None
    for attached_path in attached_files:
        cleaned_attached = clean_file_path(attached_path)
        attached_path_obj = Path(cleaned_attached)
        print(f"  Comparing with cleaned attached: {repr(cleaned_attached)}")
        print(f"  Attached filename: {repr(attached_path_obj.name)}")
        
        if cleaned_attached == cleaned_input or attached_path_obj.name == file_name_only:
            matching_file = cleaned_attached
            print(f"  ✓ MATCH FOUND!")
            break
        else:
            print(f"  ✗ No match")
    
    if matching_file:
        print(f"Result: Would read file at: {matching_file}")
    else:
        print(f"Result: File not found")