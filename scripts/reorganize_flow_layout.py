#!/usr/bin/env python3
"""
Flow Layout Reorganizer for LangBuilder

Reorganizes flow node positions to create a clean left-to-right layout with:
- Handle-to-handle alignment (straight horizontal lines between connected ports)
- Vertical separation at branch points (TRUE/FALSE paths on different rows)
- Second pass optimization for readability

Usage:
    python reorganize_flow_layout.py <flow_id> [--api-url <url>] [--dry-run]

Authentication:
    Set environment variables:
    - LANGBUILDER_API_KEY: Your LangBuilder API key
    OR
    - LANGBUILDER_USERNAME and LANGBUILDER_PASSWORD: For JWT auth
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
NODE_WIDTH = 300           # Estimated node width
HORIZONTAL_SPACING = NODE_WIDTH + (NODE_WIDTH // 2)  # Node width + half width gap = 450
VERTICAL_SPACING = 250     # Space between nodes in same column
MIN_VERTICAL_GAP = 200     # Minimum gap between nodes at same depth
START_X = 50
START_Y = 50

# Node geometry (estimated from typical LangBuilder nodes)
NODE_HEADER_HEIGHT = 50    # Height of node header/title area
HANDLE_SPACING = 45        # Vertical spacing between handles
HANDLE_START_OFFSET = 70   # Y offset from node top to first handle


def get_auth_headers(api_url: str) -> dict:
    """Get authentication headers from environment variables."""
    api_key = os.environ.get('LANGBUILDER_API_KEY')
    username = os.environ.get('LANGBUILDER_USERNAME')
    password = os.environ.get('LANGBUILDER_PASSWORD')

    if api_key:
        return {'x-api-key': api_key}
    elif username and password:
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


def get_node_handles(node: dict) -> tuple:
    """
    Extract input and output handle names from a node.

    Returns:
        (input_handles, output_handles) - lists of handle names in order
    """
    # Get output handles from outputs array
    outputs = node.get('data', {}).get('node', {}).get('outputs', [])
    output_handles = [o.get('name', '') for o in outputs]

    # Get input handles from template (fields with input_types)
    template = node.get('data', {}).get('node', {}).get('template', {})
    input_handles = []
    for field_name, field_def in template.items():
        if isinstance(field_def, dict) and field_def.get('input_types'):
            input_handles.append(field_name)

    return input_handles, output_handles


def get_handle_y_offset(handle_index: int, total_handles: int) -> float:
    """
    Calculate the Y offset of a handle from the node's top-left corner.

    In ReactFlow/LangBuilder, handles are distributed along the node edge.
    """
    if total_handles <= 1:
        return HANDLE_START_OFFSET

    return HANDLE_START_OFFSET + handle_index * HANDLE_SPACING


def build_graph(nodes: list, edges: list) -> dict:
    """
    Build comprehensive graph structure from nodes and edges.
    """
    node_lookup = {n['id']: n for n in nodes}
    node_ids = set(node_lookup.keys())

    # Get handles for each node
    node_handles = {}
    for nid, node in node_lookup.items():
        input_handles, output_handles = get_node_handles(node)
        node_handles[nid] = {
            'inputs': input_handles,
            'outputs': output_handles
        }

    # Build edge info with handle indices
    successors = {nid: [] for nid in node_ids}
    predecessors = {nid: [] for nid in node_ids}

    for edge in edges:
        src = edge.get('source')
        tgt = edge.get('target')

        if src not in node_ids or tgt not in node_ids:
            continue

        # Get handle names from edge
        src_handle_name = edge.get('data', {}).get('sourceHandle', {}).get('name', '')
        tgt_handle_name = edge.get('data', {}).get('targetHandle', {}).get('fieldName', '')

        # Get handle indices
        src_outputs = node_handles[src]['outputs']
        tgt_inputs = node_handles[tgt]['inputs']

        src_handle_idx = src_outputs.index(src_handle_name) if src_handle_name in src_outputs else 0
        tgt_handle_idx = tgt_inputs.index(tgt_handle_name) if tgt_handle_name in tgt_inputs else 0

        successors[src].append({
            'target': tgt,
            'src_handle_name': src_handle_name,
            'src_handle_idx': src_handle_idx,
            'src_handle_count': len(src_outputs),
            'tgt_handle_name': tgt_handle_name,
            'tgt_handle_idx': tgt_handle_idx,
            'tgt_handle_count': len(tgt_inputs)
        })

        predecessors[tgt].append({
            'source': src,
            'src_handle_name': src_handle_name,
            'src_handle_idx': src_handle_idx,
            'src_handle_count': len(src_outputs),
            'tgt_handle_name': tgt_handle_name,
            'tgt_handle_idx': tgt_handle_idx,
            'tgt_handle_count': len(tgt_inputs)
        })

    return {
        'node_ids': node_ids,
        'node_lookup': node_lookup,
        'node_handles': node_handles,
        'successors': successors,
        'predecessors': predecessors
    }


def calculate_depths(graph: dict) -> dict:
    """Calculate topological depth (X position) for each node."""
    node_ids = graph['node_ids']
    successors = graph['successors']
    predecessors = graph['predecessors']

    depths = {}
    in_degree = {nid: len(predecessors[nid]) for nid in node_ids}

    queue = deque()
    for nid in node_ids:
        if in_degree[nid] == 0:
            depths[nid] = 0
            queue.append(nid)

    while queue:
        current = queue.popleft()
        current_depth = depths[current]

        for edge_info in successors[current]:
            succ = edge_info['target']
            new_depth = current_depth + 1
            if succ not in depths or depths[succ] < new_depth:
                depths[succ] = new_depth

            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    for nid in node_ids:
        if nid not in depths:
            depths[nid] = 0

    return depths


def get_node_height(node: dict) -> int:
    """Estimate node height based on visible fields."""
    template = node.get('data', {}).get('node', {}).get('template', {})
    # Count visible (non-advanced) fields
    visible_fields = sum(1 for f, v in template.items()
                        if isinstance(v, dict) and not v.get('advanced', False)
                        and f not in ['_type', 'code'])
    # Base height + fields + outputs
    outputs = node.get('data', {}).get('node', {}).get('outputs', [])
    return 120 + (visible_fields * 45) + (len(outputs) * 40)


def calculate_positions(graph: dict, depths: dict) -> dict:
    """
    Calculate node positions to avoid overlaps and line crossings.

    Strategy:
    1. Group nodes by depth (column)
    2. For entry nodes, order by target handle index to avoid crossings
    3. For middle nodes, position to center among predecessors
    4. For output nodes, align with source output
    5. Stack nodes vertically with proper spacing based on node heights
    """
    node_ids = graph['node_ids']
    node_lookup = graph['node_lookup']
    successors = graph['successors']
    predecessors = graph['predecessors']

    y_positions = {}

    # Group nodes by depth
    depth_groups = {}
    for nid, d in depths.items():
        depth_groups.setdefault(d, []).append(nid)

    max_depth = max(depth_groups.keys()) if depth_groups else 0

    # === STEP 1: Order entry nodes to minimize crossings ===
    # Entry nodes should be ordered by the handle index they connect to on their target
    entry_nodes = [nid for nid in node_ids if not predecessors[nid]]

    # Priority order for Agent input handles (top to bottom in UI)
    HANDLE_PRIORITY = {
        'system_prompt': 0,      # Agent Instructions - top
        'agent_description': 1,
        'tools': 2,              # Tools - middle
        'input_value': 3,        # Input - bottom
        'input': 4,
    }

    def get_target_handle_order(nid):
        """Get the target handle position for sorting (to avoid line crossings)."""
        succs = successors[nid]
        if not succs:
            return (999, '', nid)  # No connections, put at end

        # Find the primary target connection
        min_order = (999, '')
        for edge_info in succs:
            tgt_handle_name = edge_info['tgt_handle_name']

            # Use priority if defined, otherwise use high number
            priority = HANDLE_PRIORITY.get(tgt_handle_name, 50)
            order = (priority, tgt_handle_name)

            if order < min_order:
                min_order = order

        return (*min_order, nid)

    # Sort entry nodes by their target handle position
    entry_nodes.sort(key=get_target_handle_order)

    # === STEP 2: Position entry nodes (depth 0) - stack vertically ===
    current_y = START_Y
    for nid in entry_nodes:
        y_positions[nid] = current_y
        node_height = get_node_height(node_lookup[nid])
        current_y += node_height + MIN_VERTICAL_GAP

    # === STEP 3: Position middle and output nodes (depth 1+) ===
    # For each node, check if it has a 1-to-1 connection for handle alignment
    for depth in range(1, max_depth + 1):
        if depth not in depth_groups:
            continue

        nodes_at_depth = depth_groups[depth]

        for nid in nodes_at_depth:
            preds = predecessors[nid]

            if not preds:
                y_positions[nid] = START_Y
                continue

            # Check for true 1-to-1 connection:
            # - This node has exactly ONE predecessor, AND
            # - That predecessor has exactly ONE successor (this node)
            is_one_to_one = False
            single_connection_edge = None

            if len(preds) == 1:
                edge_info = preds[0]
                pred_id = edge_info['source']
                pred_succs = successors[pred_id]

                # True 1-to-1: single predecessor with single successor
                if len(pred_succs) == 1:
                    is_one_to_one = True
                    single_connection_edge = edge_info

            if is_one_to_one and single_connection_edge:
                pred_id = single_connection_edge['source']
                # === 1-to-1 CONNECTION: Align handles for straight horizontal line ===
                pred_y = y_positions[pred_id]

                # Calculate handle Y offsets
                src_offset = get_handle_y_offset(
                    single_connection_edge['src_handle_idx'],
                    single_connection_edge['src_handle_count']
                )
                tgt_offset = get_handle_y_offset(
                    single_connection_edge['tgt_handle_idx'],
                    single_connection_edge['tgt_handle_count']
                )

                # Align: pred_y + src_offset = node_y + tgt_offset
                # So: node_y = pred_y + src_offset - tgt_offset
                y_positions[nid] = pred_y + src_offset - tgt_offset

            else:
                # === Multiple connections: Center among predecessors ===
                pred_ys = []
                for edge_info in preds:
                    pred_id = edge_info['source']
                    if pred_id in y_positions:
                        pred_node = node_lookup[pred_id]
                        pred_height = get_node_height(pred_node)
                        pred_center = y_positions[pred_id] + pred_height / 2
                        pred_ys.append(pred_center)

                if pred_ys:
                    avg_pred_center = sum(pred_ys) / len(pred_ys)
                    node_height = get_node_height(node_lookup[nid])
                    y_positions[nid] = avg_pred_center - node_height / 2
                else:
                    y_positions[nid] = START_Y

    # === STEP 5: Fill any missing positions ===
    for nid in node_ids:
        if nid not in y_positions:
            y_positions[nid] = START_Y

    return y_positions


def resolve_collisions(depths: dict, y_positions: dict, graph: dict) -> dict:
    """Ensure no nodes at the same depth overlap, using actual node heights."""
    node_lookup = graph['node_lookup']

    depth_groups = {}
    for nid, d in depths.items():
        depth_groups.setdefault(d, []).append(nid)

    for depth, nodes_at_depth in depth_groups.items():
        if len(nodes_at_depth) <= 1:
            continue

        # Sort by Y position
        nodes_at_depth.sort(key=lambda n: y_positions[n])

        # Ensure no overlap using actual node heights
        for i in range(1, len(nodes_at_depth)):
            prev_nid = nodes_at_depth[i - 1]
            curr_nid = nodes_at_depth[i]

            prev_height = get_node_height(node_lookup[prev_nid])
            min_y = y_positions[prev_nid] + prev_height + MIN_VERTICAL_GAP

            if y_positions[curr_nid] < min_y:
                y_positions[curr_nid] = min_y

    return y_positions


def optimize_layout(depths: dict, y_positions: dict, graph: dict) -> dict:
    """
    Second pass: Review and optimize layout for readability.

    1. Compact empty space
    2. Ensure sensible vertical distribution
    """
    # Normalize - shift everything to start from START_Y
    min_y = min(y_positions.values())
    if min_y != START_Y:
        offset = START_Y - min_y
        for nid in y_positions:
            y_positions[nid] += offset

    return y_positions


def calculate_new_positions(nodes: list, edges: list) -> dict:
    """Main function to calculate all node positions."""
    graph = build_graph(nodes, edges)
    depths = calculate_depths(graph)
    y_positions = calculate_positions(graph, depths)
    y_positions = resolve_collisions(depths, y_positions, graph)
    y_positions = optimize_layout(depths, y_positions, graph)

    positions = {}
    for nid in graph['node_ids']:
        positions[nid] = {
            'x': START_X + depths[nid] * HORIZONTAL_SPACING,
            'y': y_positions[nid]
        }

    return positions, graph, depths


def get_display_name(node: dict) -> str:
    """Get a readable display name for a node."""
    return node.get('data', {}).get('node', {}).get('display_name') or \
           node.get('data', {}).get('type', 'Unknown')


def reorganize_flow(flow_id: str, api_url: str, dry_run: bool = False):
    """Main function to reorganize a flow's layout."""
    print("Authenticating...")
    auth_headers = get_auth_headers(api_url)

    print(f"Fetching flow {flow_id}...")
    flow = fetch_flow(flow_id, auth_headers, api_url)

    if 'detail' in flow:
        print(f"Error fetching flow: {flow['detail']}")
        return False

    nodes = flow.get('data', {}).get('nodes', [])
    edges = flow.get('data', {}).get('edges', [])

    print(f"Found {len(nodes)} nodes and {len(edges)} edges")

    # Calculate positions
    new_positions, graph, depths = calculate_new_positions(nodes, edges)
    node_lookup = graph['node_lookup']
    predecessors = graph['predecessors']
    successors = graph['successors']

    # Display new layout
    print("\n" + "=" * 70)
    print("NEW LAYOUT (with handle alignment)")
    print("=" * 70)

    depth_groups = {}
    for nid, d in depths.items():
        depth_groups.setdefault(d, []).append(nid)

    for depth in sorted(depth_groups.keys()):
        nodes_at_depth = depth_groups[depth]
        nodes_at_depth.sort(key=lambda n: new_positions[n]['y'])

        print(f"\nColumn {depth} (x={new_positions[nodes_at_depth[0]]['x']}):")
        for nid in nodes_at_depth:
            name = get_display_name(node_lookup[nid])
            pos = new_positions[nid]

            # Show handle info
            handles = graph['node_handles'][nid]
            handle_info = f"[in:{len(handles['inputs'])} out:{len(handles['outputs'])}]"

            print(f"  y={int(pos['y']):4d}: {name:<28} {handle_info}")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return True

    # Update positions
    for node in nodes:
        nid = node['id']
        if nid in new_positions:
            node['position'] = new_positions[nid]

    print("\nUpdating flow...")
    result = update_flow(flow_id, flow, auth_headers, api_url)

    if 'detail' in result:
        print(f"Error updating flow: {result['detail']}")
        return False

    print("✓ Flow updated successfully!")
    print(f"  Edges preserved: {len(result.get('data', {}).get('edges', []))}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Reorganize LangBuilder flow layout with handle alignment'
    )
    parser.add_argument('flow_id', help='The flow ID to reorganize')
    parser.add_argument('--api-url', default=DEFAULT_API_URL,
                        help='LangBuilder API URL (default: http://localhost:8002)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show new layout without making changes')

    args = parser.parse_args()

    success = reorganize_flow(args.flow_id, args.api_url, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
