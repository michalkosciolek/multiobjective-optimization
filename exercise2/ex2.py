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

    def dfs():
        pass

    def find_best_route(
        self, shopping_list: list[str], max_time: int, purchase_time: int
    ) -> list:
        relevant_stores = self.filter_relevant_stores(shopping_list)

        distances = {}
        previous = {}

        for store in relevant_stores.keys():
            d, p = self.find_shortest_paths(store)
            distances[store] = d
            previous[store] = p

        self.dfs()

        pass


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
        edges=data["edges"],
        store_inventories=data["store_inventories"],
    )
    max_time = data["max_time"]
    purchase_time = data["purchase_time"]
    shopping_list = data["shopping_list"]

    result = graph.find_best_route(shopping_list, max_time, purchase_time)

    print("Best Route Result:")
    print(result)
