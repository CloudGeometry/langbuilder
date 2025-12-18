#!/usr/bin/env python3
"""
Flow Layout Reorganizer for LangBuilder

Reorganizes flow node positions to create a clean left-to-right layout
where each connected chain is on its own horizontal row.

Usage:
    python reorganize_flow_layout.py <flow_id> [--api-url <url>] [--dry-run]

Authentication:
    Set environment variables:
    - LANGBUILDER_API_KEY: Your LangBuilder API key
    OR
    - LANGBUILDER_USERNAME and LANGBUILDER_PASSWORD: For JWT auth

Example:
    export LANGBUILDER_API_KEY="sk-your-api-key"
    python reorganize_flow_layout.py 00e097c6-5fa4-49b3-ad37-d953e9c20b7c

    # Or with username/password:
    export LANGBUILDER_USERNAME="myuser"
    export LANGBUILDER_PASSWORD="mypassword"
    python reorganize_flow_layout.py 00e097c6-5fa4-49b3-ad37-d953e9c20b7c
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from collections import deque


# Configuration
DEFAULT_API_URL = "http://localhost:8002"

# Layout parameters
HORIZONTAL_SPACING = 450  # Space between columns (nodes in same chain)
VERTICAL_SPACING = 500    # Space between chains (rows)
START_X = 50
START_Y = 50


def get_auth_headers(api_url: str) -> dict:
    """Get authentication headers from environment variables."""
    api_key = os.environ.get('LANGBUILDER_API_KEY')
    username = os.environ.get('LANGBUILDER_USERNAME')
    password = os.environ.get('LANGBUILDER_PASSWORD')

    if api_key:
        return {'x-api-key': api_key}
    elif username and password:
        # Get JWT token
        data = f"username={username}&password={password}".encode()
        req = urllib.request.Request(f"{api_url}/api/v1/login", data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.load(resp)
                return {'Authorization': f"Bearer {result['access_token']}"}
        except urllib.error.URLError as e:
            print(f"Error authenticating: {e}")
            sys.exit(1)
    else:
        print("Error: No authentication configured.")
        print("Set LANGBUILDER_API_KEY or both LANGBUILDER_USERNAME and LANGBUILDER_PASSWORD")
        sys.exit(1)


def fetch_flow(flow_id: str, auth_headers: dict, api_url: str) -> dict:
    """Fetch flow data from the API."""
    req = urllib.request.Request(f"{api_url}/api/v1/flows/{flow_id}")
    for key, value in auth_headers.items():
        req.add_header(key, value)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {'detail': f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {'detail': str(e)}


def update_flow(flow_id: str, data: dict, auth_headers: dict, api_url: str) -> dict:
    """Update flow via the API."""
    req = urllib.request.Request(f"{api_url}/api/v1/flows/{flow_id}", method='PATCH')
    for key, value in auth_headers.items():
        req.add_header(key, value)
    req.add_header('Content-Type', 'application/json')
    req.data = json.dumps(data).encode()

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        return {'detail': f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {'detail': str(e)}


def find_connected_components(nodes: list, edges: list) -> list:
    """Find connected components (chains) in the flow graph."""
    node_ids = {n['id'] for n in nodes}

    # Build undirected adjacency
    adjacency = {nid: set() for nid in node_ids}
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source in node_ids and target in node_ids:
            adjacency[source].add(target)
            adjacency[target].add(source)

    # BFS to find components
    visited = set()
    components = []

    for nid in node_ids:
        if nid in visited:
            continue
        component = []
        queue = deque([nid])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(component)

    return components


def calculate_depths(chain_nodes: list, edges: list) -> dict:
    """Calculate topological depth for nodes within a chain."""
    chain_set = set(chain_nodes)

    # Build directed predecessors/successors within chain
    predecessors = {n: set() for n in chain_nodes}
    successors = {n: set() for n in chain_nodes}

    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source in chain_set and target in chain_set:
            predecessors[target].add(source)
            successors[source].add(target)

    # Calculate depths using BFS from entry points
    depths = {}
    in_degree = {n: len(predecessors[n]) for n in chain_nodes}

    queue = deque()
    for nid, deg in in_degree.items():
        if deg == 0:
            depths[nid] = 0
            queue.append(nid)

    while queue:
        current = queue.popleft()
        current_depth = depths[current]
        for succ in successors[current]:
            new_depth = current_depth + 1
            if succ not in depths or depths[succ] < new_depth:
                depths[succ] = new_depth
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    # Handle any remaining nodes
    for nid in chain_nodes:
        if nid not in depths:
            depths[nid] = 0

    return depths


def calculate_new_positions(nodes: list, edges: list) -> dict:
    """Calculate new positions for all nodes in a left-to-right layout."""
    # Find connected components
    components = find_connected_components(nodes, edges)

    # Sort components by size (largest first)
    components_sorted = sorted(components, key=lambda c: -len(c))

    # Calculate positions
    new_positions = {}
    chain_row = 0

    for chain in components_sorted:
        depths = calculate_depths(chain, edges)

        for nid in chain:
            depth = depths.get(nid, 0)
            x = START_X + depth * HORIZONTAL_SPACING
            y = START_Y + chain_row * VERTICAL_SPACING
            new_positions[nid] = {'x': x, 'y': y}

        chain_row += 1

    return new_positions


def reorganize_flow(flow_id: str, api_url: str, dry_run: bool = False):
    """Main function to reorganize a flow's layout."""
    print(f"Authenticating...")
    auth_headers = get_auth_headers(api_url)

    print(f"Fetching flow {flow_id}...")
    flow = fetch_flow(flow_id, auth_headers, api_url)

    if 'detail' in flow:
        print(f"Error fetching flow: {flow['detail']}")
        return False

    nodes = flow.get('data', {}).get('nodes', [])
    edges = flow.get('data', {}).get('edges', [])

    print(f"Found {len(nodes)} nodes and {len(edges)} edges")

    # Build node lookup for display names
    node_lookup = {n['id']: n for n in nodes}

    # Calculate new positions
    new_positions = calculate_new_positions(nodes, edges)

    # Display new layout
    print("\n=== NEW LAYOUT ===")
    components = find_connected_components(nodes, edges)
    components_sorted = sorted(components, key=lambda c: -len(c))

    for i, chain in enumerate(components_sorted):
        depths = calculate_depths(chain, edges)
        sorted_nodes = sorted(chain, key=lambda n: depths.get(n, 0))

        print(f"\nChain {i+1} (y={START_Y + i * VERTICAL_SPACING}):")
        for nid in sorted_nodes:
            name = node_lookup[nid]['data']['node'].get('display_name',
                   node_lookup[nid]['data']['type'])
            pos = new_positions[nid]
            print(f"  Col {depths.get(nid, 0)}: {name:<30} ({pos['x']}, {pos['y']})")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return True

    # Update node positions in flow data
    for node in nodes:
        nid = node['id']
        if nid in new_positions:
            node['position'] = new_positions[nid]

    # Update flow via API
    print(f"\nUpdating flow...")
    result = update_flow(flow_id, flow, auth_headers, api_url)

    if 'detail' in result:
        print(f"Error updating flow: {result['detail']}")
        return False

    print(f"Flow updated successfully!")
    print(f"Edges preserved: {len(result.get('data', {}).get('edges', []))}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Reorganize LangBuilder flow layout for left-to-right display'
    )
    parser.add_argument('flow_id', help='The flow ID to reorganize')
    parser.add_argument('--api-url', default=DEFAULT_API_URL,
                        help='LangBuilder API URL (default: http://localhost:8002)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show new layout without making changes')

    args = parser.parse_args()

    success = reorganize_flow(
        args.flow_id,
        args.api_url,
        args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
