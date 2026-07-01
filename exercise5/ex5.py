import argparse
import copy
import json
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONFIG = {}


@dataclass
class Genotype:
    base_assignment: dict[int, list[int]]
    modifications: list[tuple] = field(default_factory=list)
    fitness: float = float("inf")

    def __post_init__(self) -> None:
        self.base_assignment = copy.deepcopy(self.base_assignment)
        self.modifications = copy.deepcopy(self.modifications)

    def decode(self) -> dict[int, list[int]]:
        assignment = copy.deepcopy(self.base_assignment)
        node_to_courier = {
            node: courier_id
            for courier_id, nodes in assignment.items()
            for node in nodes
        }

        for modification in self.modifications:
            operation = modification[0]

            if operation == "MOVE":
                _, node, target_courier = modification
                current_courier = node_to_courier.get(node)

                if current_courier is not None and current_courier != target_courier:
                    assignment[current_courier].remove(node)
                    assignment[target_courier].append(node)
                    node_to_courier[node] = target_courier

            elif operation == "SWAP":
                _, first_node, second_node = modification
                first_courier = node_to_courier.get(first_node)
                second_courier = node_to_courier.get(second_node)

                if (
                    first_courier is not None
                    and second_courier is not None
                    and first_courier != second_courier
                ):
                    first_index = assignment[first_courier].index(first_node)
                    second_index = assignment[second_courier].index(second_node)

                    assignment[first_courier][first_index] = second_node
                    assignment[second_courier][second_index] = first_node
                    node_to_courier[first_node] = second_courier
                    node_to_courier[second_node] = first_courier

        return assignment

    def compress(self) -> None:
        self.base_assignment = self.decode()
        self.modifications = []


def get_input_filepath() -> str:
    script_dir = Path(__file__).resolve().parent
    return str(script_dir / "ex5.json")


def load_config(filepath: str) -> None:
    global CONFIG

    config_path = Path(filepath)
    if not config_path.is_absolute():
        script_dir = Path(__file__).resolve().parent
        script_path = script_dir / config_path
        if script_path.exists():
            config_path = script_path

    with open(config_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    data["coords"] = {
        int(key): tuple(value) for key, value in data["coords"].items()
    }
    CONFIG = data



def calc_dist(first_node: int, second_node: int) -> float:
    x1, y1 = CONFIG["coords"][first_node]
    x2, y2 = CONFIG["coords"][second_node]
    return math.hypot(x2 - x1, y2 - y1)


def evaluate_fitness(individual: Genotype) -> float:
    decoded_routes = individual.decode()
    total_time = 0
    penalty = 10000

    for _, route in decoded_routes.items():
        if not route:
            continue

        current_node = CONFIG["depot"]
        time_elapsed = 0
        full_path = route + [CONFIG["depot"]]

        for next_node in full_path:
            distance = calc_dist(current_node, next_node)

            if time_elapsed + distance <= CONFIG["max_operating_time"]:
                total_time += distance
                time_elapsed += distance
                current_node = next_node
            else:
                best_supply = None
                min_detour = float("inf")

                for supply_node in CONFIG["supply_nodes"]:
                    to_supply = calc_dist(current_node, supply_node)
                    from_supply = calc_dist(supply_node, next_node)

                    if time_elapsed + to_supply <= CONFIG["max_operating_time"]:
                        detour = to_supply + from_supply
                        if detour < min_detour:
                            min_detour = detour
                            best_supply = supply_node

                if best_supply is None:
                    individual.fitness = penalty
                    return penalty

                total_time += calc_dist(current_node, best_supply)
                time_elapsed = 0

                distance_from_supply = calc_dist(best_supply, next_node)
                if distance_from_supply > CONFIG["max_operating_time"]:
                    individual.fitness = penalty
                    return penalty

                total_time += distance_from_supply
                time_elapsed += distance_from_supply
                current_node = next_node

    individual.fitness = total_time
    return total_time


def create_random_individual() -> Genotype:
    base_assignment = {i: [] for i in range(CONFIG["num_couriers"])}
    shuffled_nodes = copy.deepcopy(CONFIG["demand_nodes"])
    random.shuffle(shuffled_nodes)

    for index, node in enumerate(shuffled_nodes):
        base_assignment[index % CONFIG["num_couriers"]].append(node)

    return Genotype(base_assignment, modifications=[])


def crossover(parent1: Genotype, parent2: Genotype) -> Genotype:
    child_base = copy.deepcopy(parent1.base_assignment)
    modifications1 = parent1.modifications
    modifications2 = parent2.modifications

    split1 = random.randint(0, len(modifications1)) if modifications1 else 0
    split2 = random.randint(0, len(modifications2)) if modifications2 else 0

    child_modifications = modifications1[:split1] + modifications2[split2:]
    return Genotype(child_base, child_modifications)


def mutate(individual: Genotype) -> None:
    if random.random() < 0.5:
        node = random.choice(CONFIG["demand_nodes"])
        target = random.randint(0, CONFIG["num_couriers"] - 1)
        individual.modifications.append(("MOVE", node, target))
    else:
        first_node, second_node = random.sample(CONFIG["demand_nodes"], 2)
        individual.modifications.append(("SWAP", first_node, second_node))


def run_ga(generations: int = 100, pop_size: int = 50) -> Genotype:
    population = [create_random_individual() for _ in range(pop_size)]

    for generation in range(generations):
        for individual in population:
            evaluate_fitness(individual)

        population.sort(key=lambda individual: individual.fitness)

        if generation % 10 == 0:
            for individual in population:
                individual.compress()

        next_generation = population[:5]

        while len(next_generation) < pop_size:
            parent1, parent2 = random.choices(population[:25], k=2)
            child = crossover(parent1, parent2)
            if random.random() < 0.3:
                mutate(child)
            next_generation.append(child)

        population = next_generation

        if generation % 20 == 0 or generation == generations - 1:
            print(f"Gen {generation} | Best Cost: {population[0].fitness:.2f}")

    best_individual = population[0]
    best_individual.compress()
    return best_individual


def main() -> None:
    parser = argparse.ArgumentParser(description="Courier VRP Genetic Algorithm")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=get_input_filepath(),
        help="Path to the input JSON file (default: ex5.json)",
    )
    args = parser.parse_args()

    load_config(args.input)

    best = run_ga()
    print()
    print("ALLOCATION FOUND")

    final_routes = best.decode()
    for courier_id, route in final_routes.items():
        print(f"Courier {courier_id}: Visits Demand Nodes {route}")


if __name__ == "__main__":
    main()
