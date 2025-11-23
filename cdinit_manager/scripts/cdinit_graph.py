#!/usr/bin/env python3
"""
Parse dinit service files and generate a dependency graph in hiearch YAML format.

This script traverses a set of directories, parses dinit service files,
builds a dependency graph, and outputs it in hiearch YAML format for use with hiearch.
"""

import argparse
import os
import re
import sys
import yaml


def parse_service_file(file_path):
    """
    Parse a dinit service file and extract dependencies and service type.

    Args:
        file_path (str): Path to the service file

    Returns:
        dict: A dictionary with service name, type and its dependencies
    """
    dependencies = {
        'depends-on': [],
        'depends-ms': [],
        'waits-for': [],
        'after': [],
        'before': [],
        'depends-on.d': [],
        'depends-ms.d': [],
        'waits-for.d': []
    }

    service_type = 'process'  # Default service type
    has_parameters = False  # Flag to detect if the service supports arguments

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        # Skip binary or unreadable files
        sys.stderr.write(f'Warning: Could not read file {file_path}\n')
        service_name = os.path.basename(file_path)
        service_name = service_name.split('@')[0] if '@' in service_name else service_name
        return {'name': service_name, 'type': service_type, 'dependencies': dependencies, 'has_parameters': has_parameters}

    current_line = 0
    lines = content.splitlines()

    while current_line < len(lines):
        line = lines[current_line].strip()
        current_line += 1

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Handle meta-commands (lines starting with @)
        if line.startswith('@'):
            # For @include and @include-opt, we would need to process included files
            # For now, we'll just skip them
            continue

        # Check if this line contains parameter references (like $1, $2, $3 etc.)
        if re.search(r'\$\d+', line):
            has_parameters = True

        # Match property patterns
        # Format: property = value or property: value
        match = re.match(r'^([a-zA-Z0-9._-]+)\s*([:=])\s*(.*)$', line)
        if match:
            prop_name = match.group(1).strip()
            value = match.group(3).strip()

            # Remove trailing comments
            if '#' in value:
                value = value[:value.index('#')].strip()

            # Handle service type
            if prop_name == 'type':
                service_type = value.split()[0] if value.split() else 'process'

            # Handle dependency properties
            if prop_name in dependencies:
                # Handle multi-line values if they exist
                full_value = value
                while current_line < len(lines) and lines[current_line].startswith(' '):
                    continued_line = lines[current_line].strip()
                    if continued_line:
                        full_value += ' ' + continued_line
                    current_line += 1

                # Add dependencies (space-separated values)
                deps = full_value.split()
                # Filter out parameters after @ symbol in dependency names
                # Also filter out any parameter placeholders like $1, $2, etc.
                filtered_deps = []
                for dep in deps:
                    # Remove @ parameters
                    dep = dep.split('@')[0] if '@' in dep else dep
                    # Skip parameter placeholders like $1, $2, etc.
                    if not dep.startswith('$'):
                        filtered_deps.append(dep)
                dependencies[prop_name].extend(filtered_deps)

    # Extract service name without parameters (before @ symbol)
    service_name = os.path.basename(file_path)
    service_name = service_name.split('@')[0] if '@' in service_name else service_name

    return {
        'name': service_name,
        'type': service_type,
        'dependencies': dependencies,
        'has_parameters': has_parameters
    }


def get_services_from_directory(directory):
    """
    Get all service files from a directory (non-recursive).

    Args:
        directory (str): Directory path to scan

    Returns:
        list: List of service file paths
    """
    service_files = []

    # Look for all files in the directory (not subdirectories)
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            service_files.append(item_path)

    return service_files


def expand_directory_dependencies(directory_dep_path, service_dir):
    """
    Expand directory-based dependencies by reading files in the specified directory.

    Args:
        directory_dep_path (str): Path relative to the service file
        service_dir (str): Directory containing the service file

    Returns:
        list: List of service names from the directory
    """
    # Resolve the actual directory path
    if directory_dep_path.startswith('/'):
        actual_dir = directory_dep_path
    else:
        actual_dir = os.path.join(service_dir, directory_dep_path)

    services = []
    if os.path.isdir(actual_dir):
        for item in os.listdir(actual_dir):
            if not item.startswith('.'):  # Skip hidden files/directories
                # Extract service name without parameters (before @ symbol)
                base_service_name = item.split('@')[0] if '@' in item else item
                services.append(base_service_name)

    return services


def get_style_for_service_type(service_type):
    """
    Get a hiearch style for a given service type.

    Args:
        service_type (str): Type of the service

    Returns:
        str: Style name for the service type
    """
    style_map = {
        'process': 'hh_dinit_process',
        'bgprocess': 'hh_dinit_bgprocess',
        'scripted': 'hh_dinit_scripted',
        'internal': 'hh_dinit_internal',
        'triggered': 'hh_dinit_triggered',
        'unknown': 'hh_dinit_unknown',  # For missing dependencies
    }
    return style_map.get(service_type, 'hh_dinit_unknown')


def get_edge_style_for_dependency_type(dep_type):
    """
    Get a hiearch edge style for a given dependency type.

    Args:
        dep_type (str): Type of the dependency

    Returns:
        str: Edge style name for the dependency
    """
    edge_style_map = {
        'depends-on': 'hh_dinit_depends_on',      # Standard dependency
        'depends-ms': 'hh_dinit_depends_ms',      # Milestone dependency
        'waits-for': 'hh_dinit_waits_for',        # Waits-for dependency
        'after': 'hh_dinit_after',                # Ordering dependency
    }
    return edge_style_map.get(dep_type, 'hh_dinit_depends_on')


def add_dependency_edges(service_name, dependencies, service_dir, nodes, edges):
    """Add dependency edges to the graph."""
    # Add all dependency types that create edges (hard dependencies)
    for dep_type in ['depends-on', 'depends-ms', 'waits-for']:
        for dep in dependencies[dep_type]:
            if dep.endswith('.d'):
                # This is a directory dependency
                expanded_deps = expand_directory_dependencies(dep[:-2], service_dir)
                for expanded_dep in expanded_deps:
                    # Always add the dependency as a node, regardless of whether it exists in scanned files
                    if expanded_dep not in nodes:
                        nodes[expanded_dep] = ('unknown', False)  # Default type for missing dependencies
                    edges.add((service_name, expanded_dep, dep_type))
            else:
                # Regular dependency - always add as a node even if not found in scanned files
                if dep not in nodes:
                    nodes[dep] = ('unknown', False)  # Default type for missing dependencies
                edges.add((service_name, dep, dep_type))

    # Handle 'after' dependencies (ordering, but still represent as edges)
    for dep in dependencies['after']:
        if dep not in nodes:
            nodes[dep] = ('unknown', False)  # Default type for missing dependencies
        edges.add((service_name, dep, 'after'))

    # Handle 'before' dependencies (reverse of after)
    for dep in dependencies['before']:
        if dep not in nodes:
            nodes[dep] = ('unknown', False)  # Default type for missing dependencies
        edges.add((dep, service_name, 'after'))  # before is reverse of after


def build_dependency_graph(service_files):
    """
    Build a dependency graph from service files.

    Args:
        service_files (list): List of service file paths

    Returns:
        tuple: (nodes, edges) where nodes is a dict mapping service names to types and parametric info and
               edges is a list of (source, target, dependency_type) tuples
    """
    # Dictionary to store service name -> (type, has_parameters)
    nodes = {}
    edges = set()  # Using set to avoid duplicate edges

    # First pass: collect all service names and their types and parametric information
    for service_file in service_files:
        service_info = parse_service_file(service_file)
        service_name = service_info['name']
        service_type = service_info['type']
        has_parameters = service_info['has_parameters']
        nodes[service_name] = (service_type, has_parameters)

    # Second pass: parse dependencies and build edges
    for service_file in service_files:
        service_info = parse_service_file(service_file)
        service_name = service_info['name']
        service_dir = os.path.dirname(service_file)
        dependencies = service_info['dependencies']

        add_dependency_edges(service_name, dependencies, service_dir, nodes, edges)

    return nodes, list(edges)


def generate_hiearch_format(nodes, edges, target_services=None):
    """
    Generate hiearch YAML format from nodes and edges.

    Args:
        nodes (dict): Dictionary of service names to (their types, has_parameters)
        edges (list): List of (source, target, dependency_type) tuples
        target_services (list): List of target services to create a dedicated view for (None if all services)

    Returns:
        str: hiearch YAML format string
    """
    hiearch_data = {
        'nodes': [],
        'edges': [],
        'views': []
    }

    # Add nodes with styles based on service type
    for service_name, (service_type, has_parameters) in sorted(nodes.items()):
        # Add "@" suffix to service name if it supports parameters
        display_name = service_name + "@" if has_parameters else service_name
        style = get_style_for_service_type(service_type)
        hiearch_data['nodes'].append({
            'id': [display_name, service_name],  # [label, unique id] - label shows @ if parametric, id stays the same
            'style_notag': style
        })

    # Add edges with different styles based on dependency type
    for source, target, dep_type in edges:
        edge_style = get_edge_style_for_dependency_type(dep_type)
        # Use actual node IDs in the link, not display names (the display names are for the nodes themselves)
        hiearch_data['edges'].append({
            'link': [source, target],  # Use actual node IDs, not display names
            'style': edge_style
        })

    # Create view(s) based on whether specific services were selected
    if target_services:
        # Create a dedicated view for the selected services and their dependencies
        hiearch_data['views'].append({
            'id': 'dinit_service_selection',
            'nodes': target_services,
            'neighbours': 'recursive_out',
            'style': 'hh_dinit_service_view'
        })

        # Also create an "all services" view
        hiearch_data['views'].append({
            'id': 'dinit_service_all',
            'style': 'hh_dinit_service_view',
            'tags': ['default']
        })
    else:
        # Create a default view for all services
        hiearch_data['views'].append({
            'id': 'dinit_service_all',
            'style': 'hh_dinit_service_view',
            'tags': ['default']
        })

    # Use safe_dump to avoid issues with special YAML characters
    return yaml.safe_dump(hiearch_data, default_flow_style=False, allow_unicode=True)




def main():
    """Parse command line arguments and generate the dependency graph."""
    parser = argparse.ArgumentParser(
        description='Parse dinit service files and generate a dependency graph in hiearch YAML format.'
    )
    parser.add_argument(
        '-d', '--directories',
        nargs='+',
        help='Directories to traverse for dinit service files'
    )
    parser.add_argument(
        '-s', '--services',
        nargs='*',
        help='Optional list of service names to visualize (if not provided, all services are visualized)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)',
        type=argparse.FileType('w'),
        default='-'
    )

    args = parser.parse_args()

    # Collect all service files from the provided directories
    service_files = []
    for directory in args.directories:
        if os.path.isdir(directory):
            service_files.extend(get_services_from_directory(directory))
        else:
            sys.stderr.write(f'Warning: {directory} is not a directory, skipping.\n')

    # Build the dependency graph
    nodes, edges = build_dependency_graph(service_files)

    # Generate and output the hiearch format to the specified output
    # Service filtering is handled automatically by hiearch based on view parameters
    hiearch_output = generate_hiearch_format(nodes, edges, target_services=args.services)

    args.output.write(hiearch_output)

    if args.output != '-':
        args.output.close()


if __name__ == '__main__':
    main()
