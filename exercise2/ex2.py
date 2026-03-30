import json
import os
import sys


class StoresGraph:
    def __init__(self, num_nodes: int, edges=None, store_inventories=None, home_node=0):
        self.num_nodes = num_nodes
        self.home_node = home_node
        self.adj_list = self._build_adjacency_list(edges or [])
        self.store_inventories = self._build_store_inventories(store_inventories or {})

    def _build_adjacency_list(
        self, edges: list[list[int]]
    ) -> list[list[tuple[int, int]]]:
        adjacency = [[] for _ in range(self.num_nodes)]

        if not edges:
            return adjacency

        for start, end, weight in edges:
            adjacency[start].append((end, weight))
            adjacency[end].append((start, weight))

        return adjacency

    def _build_store_inventories(self, store_inventories: dict) -> dict[int, list[str]]:
        return {
            int(store): inventory
            for store, inventory in (store_inventories or {}).items()
        }

    def filter_relevant_stores(self, shopping_list: list[str]) -> dict[int, set[str]]:
        filtered_stores = {}
        shopping_set = set(shopping_list)

        for store, inventory in self.store_inventories.items():
            relevant_items = set(inventory).intersection(shopping_set)
            if relevant_items and store != self.home_node:
                filtered_stores[store] = relevant_items

        return filtered_stores

    def find_shortest_paths(
        self, start_node: int
    ) -> tuple[dict[int, float], dict[int, int | None]]:
        distances = {i: float("inf") for i in range(self.num_nodes)}
        distances[start_node] = 0
        prev = {i: None for i in range(self.num_nodes)}
        visited = set()

        while len(visited) < self.num_nodes:
            current_node = None
            current_dist = float("inf")

            for node in range(self.num_nodes):
                if node not in visited and distances[node] < current_dist:
                    current_node = node
                    current_dist = distances[node]

            if current_node is None:
                break

            visited.add(current_node)

            for neighbor, weight in self.adj_list[current_node]:
                distance = current_dist + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    prev[neighbor] = current_node

        return distances, prev

    def _dfs_search(
        self,
        current_node: int,
        current_time: int,
        visited_stores: set,
        acquired_items: set,
        current_sequence: list,
        filtered_stores: dict,
        dist: dict,
        max_time: int,
        purchase_time: int,
        best_state: dict,
    ):
        """
        DFS with backtracking to find optimal shopping route.

        Args:
            current_node: Current location
            current_time: Time elapsed so far
            visited_stores: Set of already visited stores
            acquired_items: Set of items acquired so far
            current_sequence: Current route sequence
            filtered_stores: Dict of store -> items available
            dist: Distance matrix between nodes
            max_time: Maximum time allowed
            purchase_time: Fixed time per store visit
            best_state: Dict tracking best solution (modified in-place)
        """
        # Update best solution if current path has more items
        if len(acquired_items) > best_state["items_count"]:
            best_state["items_count"] = len(acquired_items)
            best_state["sequence"] = list(current_sequence)
            best_state["items"] = set(acquired_items)

        # Generate candidate stores
        candidates = []
        for store, inventory in filtered_stores.items():
            if store not in visited_stores:
                new_items = inventory - acquired_items
                if not new_items:
                    continue

                travel_time = dist[current_node][store]
                time_to_home = dist[store][self.home_node]

                # Safety check in case a store is unreachable
                if travel_time == float("inf") or time_to_home == float("inf"):
                    continue

                total_time_needed = (
                    current_time + travel_time + purchase_time + time_to_home
                )

                if total_time_needed <= max_time:
                    candidates.append((store, new_items, travel_time))

        # Sort by number of new items (descending) - prioritization
        candidates.sort(key=lambda x: len(x[1]), reverse=True)

        # Explore each candidate with backtracking
        for store, new_items, travel_time in candidates:
            visited_stores.add(store)
            self._dfs_search(
                store,
                current_time + travel_time + purchase_time,
                visited_stores,
                acquired_items.union(new_items),
                current_sequence + [store],
                filtered_stores,
                dist,
                max_time,
                purchase_time,
                best_state,
            )
            visited_stores.remove(store)

    def find_best_route(
        self, shopping_list: list[str], max_time: int, purchase_time: int
    ) -> dict:
        """
        Find the best shopping route that maximizes items purchased within time limit.

        Returns:
            dict with 'route', 'items', and 'time_used' keys
        """
        filtered_stores = self.filter_relevant_stores(shopping_list)

        if not filtered_stores:
            return {
                "route": [self.home_node, self.home_node],
                "items": [],
                "time_used": 0,
            }

        # Build distance matrix between all relevant nodes
        relevant_nodes = list(filtered_stores.keys()) + [self.home_node]
        dist = {}

        for node in relevant_nodes:
            distances, _ = self.find_shortest_paths(node)
            dist[node] = distances

        # State tracker for DFS (modified in-place)
        best_state = {"items_count": -1, "sequence": [], "items": set()}

        # Start DFS from home node
        self._dfs_search(
            self.home_node,
            0,
            {self.home_node},
            set(),
            [self.home_node],
            filtered_stores,
            dist,
            max_time,
            purchase_time,
            best_state,
        )

        # Complete the route by returning home
        best_state["sequence"].append(self.home_node)

        # Calculate final time used
        time_used = 0
        for i in range(len(best_state["sequence"]) - 1):
            time_used += dist[best_state["sequence"][i]][best_state["sequence"][i + 1]]
            # Add purchase time for intermediate stores (not home)
            if i > 0 and i < len(best_state["sequence"]) - 1:
                time_used += purchase_time

        return {
            "route": best_state["sequence"],
            "items": sorted(list(best_state["items"])),
            "time_used": time_used,
        }


def read_input(file_dir: str) -> dict:
    with open(file_dir, "r") as file:
        data = json.load(file)
    return data


if __name__ == "__main__":
    default_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "shopping_data.json"
    )
    file_dir = sys.argv[1] if len(sys.argv) > 1 else default_file
    data = read_input(file_dir)

    graph = StoresGraph(
        num_nodes=data["num_nodes"],
        home_node=data["home_node"],
        edges=data["adj_list"],  # Fixed: use 'adj_list' from JSON
        store_inventories=data["store_inventories"],
    )
    max_time = data["max_time"]
    purchase_time = data["purchase_time"]
    shopping_list = data["shopping_list"]

    result = graph.find_best_route(shopping_list, max_time, purchase_time)

    print("=" * 60)
    print("SHOPPING OPTIMIZATION RESULTS")
    print("=" * 60)
    print(f"Shopping List: {', '.join(shopping_list)}")
    print(f"Max Time Available: {max_time} units")
    print(f"Purchase Time per Store: {purchase_time} units")
    print()
    print(f"Items Acquired: {len(result['items'])}/{len(shopping_list)}")
    print(f"Items: {', '.join(result['items']) if result['items'] else 'None'}")
    print()
    print(f"Route: {' -> '.join(map(str, result['route']))}")
    print(f"Time Used: {result['time_used']}/{max_time} units")
    print("=" * 60)
