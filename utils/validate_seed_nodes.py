#!/usr/bin/env python3
"""
Validate seed-nodes.json against its JSON schema.

This script validates the seed-nodes.json file located in the project root
against the JSON schema defined in utils/seed_nodes_schema.json.
"""

import json
import sys
import os
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("Error: jsonschema package is required. Install it with:")
    print("pip install jsonschema")
    sys.exit(1)


def get_project_root():
    """Get the project root directory (parent of utils directory)."""
    return Path(__file__).parent.parent


def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def validate_seed_nodes(seed_nodes_path=None, schema_path=None):
    """
    Validate seed-nodes.json against its schema.
    
    Args:
        seed_nodes_path: Path to seed-nodes.json (default: project_root/seed-nodes.json)
        schema_path: Path to schema file (default: utils/seed_nodes_schema.json)
    
    Returns:
        bool: True if validation passes, False otherwise
    """
    project_root = get_project_root()
    
    # Set default paths if not provided
    if seed_nodes_path is None:
        seed_nodes_path = project_root / "seed-nodes.json"
    if schema_path is None:
        schema_path = project_root / "utils" / "seed_nodes_schema.json"
    
    print(f"Validating: {seed_nodes_path}")
    print(f"Schema: {schema_path}")
    print("-" * 50)
    
    # Load schema
    schema = load_json_file(schema_path)
    if schema is None:
        return False
    
    # Load seed nodes data
    seed_nodes = load_json_file(seed_nodes_path)
    if seed_nodes is None:
        return False
    
    try:
        # Validate the schema itself first
        jsonschema.Draft202012Validator.check_schema(schema)
        print("✓ Schema is valid")
        
        # Validate the seed nodes data against the schema
        validate(instance=seed_nodes, schema=schema)
        print("✓ Seed nodes file is valid!")
        print(f"✓ Found {len(seed_nodes)} seed nodes")
        
        # Print summary of nodes
        for i, node in enumerate(seed_nodes, 1):
            host = node.get('host', 'unknown')
            name = node.get('name', f'node-{i}')
            netid = node.get('netid', 'unknown') # 14428 is the max netid if rpcport is 7783 lookup max_netid in kdf repo 
            contact_count = len(node.get('contact', []))
            print(f"  {i}. {name} ({host}) - netid: {netid} - {contact_count} contact(s)")
        
        return True
        
    except SchemaError as e:
        print(f"✗ Schema validation error: {e}")
        return False
    except ValidationError as e:
        print(f"✗ Validation failed: {e.message}")
        if e.absolute_path:
            print(f"  Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        if e.instance:
            print(f"  Invalid value: {e.instance}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main function to run validation."""
    print("Komodo Seed Nodes Validator")
    print("=" * 50)
    
    # Parse command line arguments
    seed_nodes_path = None
    schema_path = None
    
    if len(sys.argv) > 1:
        seed_nodes_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        schema_path = Path(sys.argv[2])
    
    # Run validation
    is_valid = validate_seed_nodes(seed_nodes_path, schema_path)
    
    print("-" * 50)
    if is_valid:
        print("🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 