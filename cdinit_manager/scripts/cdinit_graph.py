#!/usr/bin/env python3
"""
Parse dinit service files and generate a dependency graph in Graphviz dot format.

This script traverses a set of directories, parses dinit service files,
builds a dependency graph, and outputs it in Graphviz dot format.
"""

import argparse
import os
import re
import sys


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

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        # Skip binary or unreadable files
        sys.stderr.write(f'Warning: Could not read file {file_path}\n')
        service_name = os.path.basename(file_path)
        service_name = service_name.split('@')[0] if '@' in service_name else service_name
        return {'name': service_name, 'type': service_type, 'dependencies': dependencies}

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

        # Match property patterns
        # Format: property = value or property: value
        match = re.match(r'^([a-zA-Z0-9._-]+)\s*([:=])\s*(.*)$', line)
        if match:
            prop_name = match.group(1).strip()
            # separator = match.group(2)  # This variable was unused
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
                filtered_deps = [dep.split('@')[0] if '@' in dep else dep for dep in deps]
                dependencies[prop_name].extend(filtered_deps)

    # Extract service name without parameters (before @ symbol)
    service_name = os.path.basename(file_path)
    service_name = service_name.split('@')[0] if '@' in service_name else service_name

    return {
        'name': service_name,
        'type': service_type,
        'dependencies': dependencies
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


def get_color_for_service_type(service_type):
    """
    Get a color for a given service type.

    Args:
        service_type (str): Type of the service

    Returns:
        str: Color name/HEX code for the service type
    """
    color_map = {
        'process': 'lightblue',
        'bgprocess': 'lightgreen',
        'scripted': 'lightyellow',
        'internal': 'lightgray',
        'triggered': 'lightpink',
        'unknown': 'white',  # For missing dependencies
    }
    return color_map.get(service_type, 'white')


def get_arrowhead_for_dependency_type(dep_type):
    """
    Get an arrowhead type for a given dependency type.

    Args:
        dep_type (str): Type of the dependency

    Returns:
        str: Arrowhead type for the dependency
    """
    arrowhead_map = {
        'depends-on': 'normal',      # Standard dependency
        'depends-ms': 'dot',         # Milestone dependency
        'waits-for': 'diamond',      # Waits-for dependency
        'after': 'tee',              # Ordering dependency
    }
    return arrowhead_map.get(dep_type, 'normal')


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
                        nodes[expanded_dep] = 'unknown'  # Default type for missing dependencies
                    edges.add((service_name, expanded_dep, dep_type))
            else:
                # Regular dependency - always add as a node even if not found in scanned files
                if dep not in nodes:
                    nodes[dep] = 'unknown'  # Default type for missing dependencies
                edges.add((service_name, dep, dep_type))

    # Handle 'after' dependencies (ordering, but still represent as edges)
    for dep in dependencies['after']:
        if dep not in nodes:
            nodes[dep] = 'unknown'  # Default type for missing dependencies
        edges.add((service_name, dep, 'after'))

    # Handle 'before' dependencies (reverse of after)
    for dep in dependencies['before']:
        if dep not in nodes:
            nodes[dep] = 'unknown'  # Default type for missing dependencies
        edges.add((dep, service_name, 'after'))  # before is reverse of after


def build_dependency_graph(service_files):
    """
    Build a dependency graph from service files.

    Args:
        service_files (list): List of service file paths

    Returns:
        tuple: (nodes, edges) where nodes is a dict mapping service names to types and
               edges is a list of (source, target, dependency_type) tuples
    """
    nodes = {}  # Dictionary to store service name -> type mapping
    edges = set()  # Using set to avoid duplicate edges

    # First pass: collect all service names and their types
    for service_file in service_files:
        service_info = parse_service_file(service_file)
        service_name = service_info['name']
        service_type = service_info['type']
        nodes[service_name] = service_type

    # Second pass: parse dependencies and build edges
    for service_file in service_files:
        service_info = parse_service_file(service_file)
        service_name = service_info['name']
        service_dir = os.path.dirname(service_file)
        dependencies = service_info['dependencies']

        add_dependency_edges(service_name, dependencies, service_dir, nodes, edges)

    return nodes, list(edges)


def generate_dot_format(nodes, edges):
    """
    Generate Graphviz dot format from nodes and edges.

    Args:
        nodes (dict): Dictionary of service names to their types
        edges (list): List of (source, target, dependency_type) tuples

    Returns:
        str: Graphviz dot format string
    """
    dot_lines = ['digraph DinitServices {']
    dot_lines.append('    rankdir=TB;')
    dot_lines.append('    node [shape=box, style=rounded];')

    # Add nodes with colors based on service type
    for service_name, service_type in sorted(nodes.items()):
        # Escape special characters for Graphviz
        escaped_name = service_name.replace('"', '\\"')
        color = get_color_for_service_type(service_type)
        dot_lines.append(f'    "{escaped_name}" [label="{escaped_name}", fillcolor="{color}", style="rounded,filled"];')

    # Add edges with different arrowheads based on dependency type
    for source, target, dep_type in edges:
        escaped_source = source.replace('"', '\\"')
        escaped_target = target.replace('"', '\\"')
        arrowhead = get_arrowhead_for_dependency_type(dep_type)
        dot_lines.append(f'    "{escaped_source}" -> "{escaped_target}" [arrowhead="{arrowhead}"];')

    dot_lines.append('}')

    return '\n'.join(dot_lines)


def filter_graph_to_services(nodes, edges, target_services):
    """
    Filter the dependency graph to only include specified services and their dependencies.
    Only the selected services and services they depend on should be visualized,
    services that depend on selected services should be omitted.

    Args:
        nodes (dict): Dictionary mapping service names to types
        edges (list): List of (source, target, dependency_type) tuples
        target_services (list): List of service names to include in the filtered graph

    Returns:
        tuple: (filtered_nodes, filtered_edges) containing only the services and their dependencies
    """
    # Start with the target services
    all_relevant_services = set(target_services)

    # Keep adding dependencies until no new ones are found
    # Only add services that the current services depend ON (not services that depend on them)
    changed = True
    while changed:
        changed = False
        new_services = set()

        for source, target, dep_type in edges:
            # Only add the target if source is in our graph and target is not
            # This means we're following dependency arrows FROM our selected services
            if source in all_relevant_services and target not in all_relevant_services:
                new_services.add(target)
                changed = True

        all_relevant_services.update(new_services)

    # Filter nodes to only include relevant services
    filtered_nodes = {name: nodes[name] for name in all_relevant_services if name in nodes}

    # Filter edges to only include those between relevant services
    # Only keep edges where both source and target are in our relevant services set
    filtered_edges = [
        (source, target, dep_type)
        for source, target, dep_type in edges
        if source in all_relevant_services and target in all_relevant_services
    ]

    return filtered_nodes, filtered_edges


def main():
    """Parse command line arguments and generate the dependency graph."""
    parser = argparse.ArgumentParser(
        description='Parse dinit service files and generate a dependency graph in Graphviz dot format.'
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

    # If specific service names were provided, filter the graph to only include those services and their dependencies
    if args.services:
        nodes, edges = filter_graph_to_services(nodes, edges, args.services)

    # Generate and output the dot format to the specified output
    dot_output = generate_dot_format(nodes, edges)
    args.output.write(dot_output)

    if args.output != '-':
        args.output.close()


if __name__ == '__main__':
    main()
