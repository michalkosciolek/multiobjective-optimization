from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from random import Random
from typing import Iterable


@dataclass(frozen=True)
class Individual:
    genes: str
    fitness: int


def get_input_filepath() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "ex4.json")


def read_input(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_individual(chromosome_length: int, rng: Random) -> Individual:
    genes = "".join(str(rng.randint(0, 1)) for _ in range(chromosome_length))
    return Individual(genes=genes, fitness=genes.count("1"))


def evaluate_individual(genes: str) -> Individual:
    return Individual(genes=genes, fitness=genes.count("1"))


def generate_population(
    population_size: int, chromosome_length: int, rng: Random
) -> list[Individual]:
    return [generate_individual(chromosome_length, rng) for _ in range(population_size)]


def rank_selection(
    population: list[Individual], selection_size: int, rng: Random
) -> list[Individual]:
    if not population:
        return []

    ranked_population = sorted(
        population, key=lambda individual: individual.fitness, reverse=True
    )
    population_size = len(ranked_population)
    rank_weights = list(range(population_size, 0, -1))
    total_weight = population_size * (population_size + 1) / 2

    selected: list[Individual] = []
    for _ in range(selection_size):
        threshold = rng.random() * total_weight
        cumulative_weight = 0.0
        for individual, weight in zip(ranked_population, rank_weights):
            cumulative_weight += weight
            if threshold < cumulative_weight:
                selected.append(individual)
                break

    return selected


def crossover(
    parents: list[Individual],
    offspring_size: int,
    crossover_rate: float,
    rng: Random,
) -> list[Individual]:
    if not parents:
        return []

    offspring: list[Individual] = []
    parent_cycle = parents.copy()
    rng.shuffle(parent_cycle)

    while len(offspring) < offspring_size:
        parent1 = parent_cycle[len(offspring) % len(parent_cycle)]
        parent2 = parent_cycle[(len(offspring) + 1) % len(parent_cycle)]

        if len(parent1.genes) < 2 or rng.random() > crossover_rate:
            offspring.append(evaluate_individual(parent1.genes))
            continue

        crossover_point = rng.randint(1, len(parent1.genes) - 1)
        child_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        offspring.append(evaluate_individual(child_genes))

    return offspring


def mutate(
    individuals: Iterable[Individual], mutation_rate: float, rng: Random
) -> list[Individual]:
    mutated_population: list[Individual] = []

    for individual in individuals:
        mutated_genes = [
            str(1 - int(gene)) if rng.random() < mutation_rate else gene
            for gene in individual.genes
        ]
        mutated_population.append(evaluate_individual("".join(mutated_genes)))

    return mutated_population


def format_population(label: str, population: list[Individual]) -> str:
    lines = [label]
    for index, individual in enumerate(population, start=1):
        lines.append(f"{index:02d}. {individual.genes} | fitness={individual.fitness}")
    return "\n".join(lines)


def main() -> None:
    config = read_input(get_input_filepath())

    rng = Random()
    population_size = config["population_size"]
    chromosome_length = config["chromosome_length"]
    selection_size = config["selection_size"]
    offspring_size = config["offspring_size"]
    crossover_rate = config["crossover_rate"]
    mutation_rate = config["mutation_rate"]

    population = generate_population(population_size, chromosome_length, rng)
    selected = rank_selection(population, selection_size, rng)
    offspring = crossover(selected, offspring_size, crossover_rate, rng)
    mutated = mutate(offspring, mutation_rate, rng)

    print(format_population("Initial population", population))
    print()
    print(format_population("Rank-selected individuals", selected))
    print()
    print(format_population("Offspring after crossover", offspring))
    print()
    print(format_population("Population after mutation", mutated))


if __name__ == "__main__":
    main()
