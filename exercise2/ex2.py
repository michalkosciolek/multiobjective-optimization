import json
import os
import sys


class ShoppingState:
    def __init__(self, items_count: int, sequence: list[int], items: set[str]):
        self.items_count = items_count
        self.sequence = sequence
        self.items = items


class ShoppingResults:
    def __init__(
        self,
        route: list[int],
        items: list[str],
        time_used: int,
    ):
        self.route = route
        self.items = items
        self.time_used = time_used

    def print_results(self):
        print("=" * 60)
        print("SHOPPING RESULTS")
        print("=" * 60)
        print(f"Items: {', '.join(self.items) if self.items else 'None'}")
        print()
        print(f"Shops visited: {' -> '.join(map(str, self.route))}")
        print(f"Time Used: {self.time_used} units")
        print("=" * 60)


class StoresGraph:
    def __init__(
        self,
        num_nodes: int,
        edges=None,
        store_inventories=None,
        home_node=0,
        purchase_time=0,
    ):
        self.num_nodes = num_nodes
        self.home_node = home_node
        self.purchase_time = purchase_time
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

    def _dfs_search(
        self,
        current_node: int,
        current_time: int,
        visited_stores: set[int],
        acquired_items: set[str],
        current_sequence: list[int],
        filtered_stores: dict[int, set[str]],
        dist: dict[int, dict[int, float]],
        max_time: int,
        best_state: ShoppingState,
    ):
        if len(acquired_items) > best_state.items_count:
            best_state.items_count = len(acquired_items)
            best_state.sequence = list(current_sequence)
            best_state.items = set(acquired_items)

        candidates = []
        for store, inventory in filtered_stores.items():
            if store in visited_stores:
                continue

            new_items = inventory - acquired_items
            if not new_items:
                continue

            travel_time = dist[current_node][store]
            time_to_home = dist[store][self.home_node]

            total_time_needed = (
                current_time + travel_time + self.purchase_time + time_to_home
            )

            if total_time_needed <= max_time:
                candidates.append((store, new_items, travel_time))

        for store, new_items, travel_time in candidates:
            visited_stores.add(store)
            self._dfs_search(
                store,
                current_time + travel_time + self.purchase_time,
                visited_stores,
                acquired_items.union(new_items),
                current_sequence + [store],
                filtered_stores,
                dist,
                max_time,
                best_state,
            )
            visited_stores.remove(store)

    def _filter_relevant_stores(self, shopping_list: list[str]) -> dict[int, set[str]]:
        filtered_stores = {}
        shopping_set = set(shopping_list)

        for store, inventory in self.store_inventories.items():
            relevant_items = set(inventory).intersection(shopping_set)
            if relevant_items and store != self.home_node:
                filtered_stores[store] = relevant_items

        return filtered_stores

    def _build_distance_matrix(
        self, filtered_stores: list[int]
    ) -> dict[int, dict[int, float]]:
        relevant_nodes = list(filtered_stores.keys()) + [self.home_node]
        distances = {}

        for node in relevant_nodes:
            current_dist = self._find_shortest_paths(node)
            distances[node] = current_dist

        return distances

    def _find_shortest_paths(self, start_node: int) -> dict[int, float]:
        distances = {i: float("inf") for i in range(self.num_nodes)}
        distances[start_node] = 0
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

        return distances

    def _calculate_time_used(
        self, best_state: ShoppingState, distances: dict[int, dict[int, float]]
    ) -> int:
        time_used = 0
        for i in range(len(best_state.sequence) - 1):
            time_used += distances[best_state.sequence[i]][best_state.sequence[i + 1]]
            if i > 0 and i < len(best_state.sequence) - 1:
                time_used += self.purchase_time
        return time_used

    def find_best_route(
        self, shopping_list: list[str], max_time: int
    ) -> ShoppingResults:
        filtered_stores = self._filter_relevant_stores(shopping_list)

        if not filtered_stores:
            return ShoppingResults(
                route=[self.home_node, self.home_node],
                items=[],
                time_used=0,
            )

        distances = self._build_distance_matrix(filtered_stores)

        best_state = ShoppingState(items_count=-1, sequence=[], items=set())

        self._dfs_search(
            self.home_node,
            0,
            {self.home_node},
            set(),
            [self.home_node],
            filtered_stores,
            distances,
            max_time,
            best_state,
        )

        best_state.sequence.append(self.home_node)

        time_used = self._calculate_time_used(best_state, distances)

        return ShoppingResults(
            route=best_state.sequence,
            items=best_state.items,
            time_used=time_used,
        )


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
        purchase_time=data["purchase_time"],
        edges=data["edges"],
        store_inventories=data["store_inventories"],
    )
    max_time = data["max_time"]
    shopping_list = data["shopping_list"]

    result = graph.find_best_route(shopping_list, max_time)
    result.print_results()
