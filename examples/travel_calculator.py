#!/usr/bin/env python3
"""
Travel time calculator using ORBIS network data.

This example demonstrates how to use the travel network data
to calculate travel times between Roman cities.
"""

import heapq
import sqlite3
from collections import defaultdict
from pathlib import Path


def load_network(db_path: Path) -> dict:
    """Load travel network from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build adjacency list
    graph = defaultdict(list)

    cursor.execute("""
        SELECT source_location_id, target_location_id,
               source_name, target_name,
               distance_km, travel_days_foot, travel_days_horse
        FROM travel_network
    """)

    for row in cursor.fetchall():
        source_id, target_id, source_name, target_name, km, days_foot, days_horse = row
        graph[source_id].append({
            "target": target_id,
            "target_name": target_name,
            "distance_km": km,
            "days_foot": days_foot or km / 25,  # Default: 25 km/day on foot
            "days_horse": days_horse or km / 50,  # Default: 50 km/day on horse
        })
        # Add reverse edge (roads work both ways)
        graph[target_id].append({
            "target": source_id,
            "target_name": source_name,
            "distance_km": km,
            "days_foot": days_foot or km / 25,
            "days_horse": days_horse or km / 50,
        })

    # Also load location names
    names = {}
    cursor.execute("SELECT id, name_latin FROM locations")
    for row in cursor.fetchall():
        names[row[0]] = row[1]

    conn.close()
    return graph, names


def dijkstra(graph: dict, start: str, end: str, mode: str = "days_foot"):
    """Find shortest path using Dijkstra's algorithm."""
    distances = {start: 0}
    previous = {start: None}
    pq = [(0, start)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            # Reconstruct path
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = previous[node]
            return distances[end], path[::-1]

        for edge in graph.get(current, []):
            neighbor = edge["target"]
            weight = edge[mode]
            if weight is None:
                continue

            distance = current_dist + weight

            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))

    return None, []


def find_location_id(conn, name: str) -> str | None:
    """Find location ID by name (Latin or modern)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM locations
        WHERE LOWER(name_latin) LIKE LOWER(?)
        OR LOWER(name_modern) LIKE LOWER(?)
        LIMIT 1
    """, (f"%{name}%", f"%{name}%"))
    row = cursor.fetchone()
    return row[0] if row else None


def main():
    db_path = Path("./my_database.sqlite")

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        print("Run 'roma-data run' first to generate the database.")
        return

    print("Loading travel network...")
    graph, names = load_network(db_path)

    if not graph:
        print("No travel network data found.")
        print("Make sure ORBIS source is enabled when running the pipeline.")
        return

    print(f"Loaded {len(graph)} nodes in travel network.")

    # Example routes
    routes = [
        ("orbis_1", "orbis_50"),  # Roma to destination
        ("orbis_1", "orbis_100"),
    ]

    for start, end in routes:
        if start not in graph or end not in graph:
            continue

        start_name = names.get(start, start)
        end_name = names.get(end, end)

        print(f"\n{'='*50}")
        print(f"Route: {start_name} -> {end_name}")

        # Calculate by foot
        days_foot, path_foot = dijkstra(graph, start, end, "days_foot")
        if days_foot:
            print(f"\nBy foot ({days_foot:.1f} days):")
            for i, node in enumerate(path_foot):
                name = names.get(node, node)
                print(f"  {i+1}. {name}")

        # Calculate by horse
        days_horse, path_horse = dijkstra(graph, start, end, "days_horse")
        if days_horse:
            print(f"\nBy horse ({days_horse:.1f} days):")
            for i, node in enumerate(path_horse):
                name = names.get(node, node)
                print(f"  {i+1}. {name}")


if __name__ == "__main__":
    main()
