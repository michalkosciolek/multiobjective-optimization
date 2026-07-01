# Exercise 5 - Genetic Algorithm for Courier Allocation

## Problem Summary

This task asks for a program that uses a genetic algorithm to assign demand nodes to couriers so that every demand node is visited exactly once by some courier, while supply nodes may be visited whenever needed for refueling.

The graph contains:

- **Demand nodes**: nodes that must be visited by couriers.
- **Supply nodes**: nodes where a courier can refuel.
- **Edge weights**: travel time between nodes, computed from coordinates as Euclidean distance.
- **Courier limit**: every courier has a maximum operating time before refueling is required.

The goal of the genetic algorithm is to find a low-cost allocation of demand nodes to couriers.

## How the Algorithm Works

The solution uses a standard genetic algorithm loop:

1. Create an initial population of candidate allocations.
2. Evaluate each candidate with a fitness function.
3. Keep the best candidates.
4. Generate new candidates with crossover and mutation.
5. Repeat for many generations.

The best candidate found at the end is printed as the final courier allocation.

## Representation of a Solution

The implementation uses a two-level chromosome structure.

### Gene

A gene represents an assignment or modification related to courier routes.

The first gene is the **base assignment**:

- a mapping from courier identifiers to lists of demand nodes.
- this is the initial distribution of demand nodes among couriers.

Other genes are stored as **modifications**:

- `MOVE`: move one demand node to another courier.
- `SWAP`: swap two demand nodes between couriers.

This matches the task description:

- the first gene stores couriers and their visited nodes,
- later genes modify the previously made assignment.

### Genotype

A genotype is the full chromosome.

In this implementation it contains:

- `base_assignment`: the first gene,
- `modifications`: a sequence of changes applied on top of the base assignment,
- `fitness`: the total travel cost of the decoded allocation.

To evaluate a genotype, the algorithm first decodes it into the final assignment of demand nodes to couriers.

## Decoding the Genotype

The `decode()` method starts from the base assignment and applies the modifications in order.

### MOVE modification

A `MOVE` gene has the form:

```python
("MOVE", node, target_courier)
```

It means:

- find the courier currently owning `node`,
- remove that node from the current courier route,
- append it to the target courier route.

### SWAP modification

A `SWAP` gene has the form:

```python
("SWAP", node1, node2)
```

It means:

- find the couriers that currently own the two nodes,
- exchange the nodes between those couriers.

### Why decoding matters

This approach makes the chromosome compact:

- the base assignment gives a valid starting point,
- modifications store only differences from that base.

The `compress()` method periodically re-encodes the current decoded solution back into the base assignment and clears the modification list. This keeps chromosomes from growing too long over many generations.

## Fitness Evaluation

The fitness function measures the total travel time of all couriers.

### Route construction

For each courier:

- start from the depot,
- visit all assigned demand nodes in the order stored in the route,
- return to the depot.

So each courier route is treated as:

```python
[depot, demand_1, demand_2, ..., demand_k, depot]
```

### Travel feasibility

Each courier can travel only up to `max_operating_time` without refueling.

For every next step in the route, the algorithm checks whether the courier can go directly from the current node to the next node.

- If yes, the distance is added to the total travel time.
- If not, the algorithm tries to detour through a supply node.

### Refueling logic

When direct travel is not possible, the algorithm searches all supply nodes and selects the best one that:

- is reachable before the courier runs out of operating time,
- minimizes the detour cost `current -> supply -> next`.

If no supply node is reachable, the genotype is considered infeasible and receives a large penalty.

If the best supply node still cannot reach the next node directly, the genotype also receives the penalty.

### Penalty value

Infeasible solutions get a fitness of `10000`.

This ensures that valid routes are always preferred over invalid ones.

## Genetic Operators

### Initial population

The initial population is generated randomly.

Demand nodes are shuffled and distributed evenly among couriers so that every demand node is assigned exactly once.

This guarantees that the initial solutions already satisfy the coverage constraint: every demand node is visited by one courier.

### Crossover

Crossover combines the modifications of two parents.

The implementation:

- copies the base assignment from the first parent,
- takes a prefix of the first parent’s modifications,
- takes a suffix of the second parent’s modifications,
- merges them into one child.

This preserves the idea that the genotype is a base solution plus changes.

### Mutation

Mutation introduces variation.

There are two possible mutation types:

- randomly move one demand node to another courier,
- swap two demand nodes.

Mutation is applied with probability `0.3` to each child.

## Main Evolution Loop

The GA runs for a fixed number of generations.

For each generation:

1. Evaluate the fitness of every individual.
2. Sort the population by fitness.
3. Keep the top 5 individuals unchanged (elitism).
4. Build the rest of the next generation using crossover and mutation.
5. Every 10 generations, compress individuals to keep chromosomes shorter.
6. Print progress every 20 generations.

This gives the algorithm a balance of:

- **exploitation**: preserving the best current solutions,
- **exploration**: generating new solutions through recombination and mutation.

## Why This Matches the Task

This solution matches the assignment requirements in the following way:

- **Demand nodes are always assigned** because the base genotype is built from all demand nodes.
- **Supply nodes are optional** because they are only used during fitness evaluation when refueling is needed.
- **Couriers have limited operating time** and must refuel at supply nodes when necessary.
- **A genetic algorithm is used** with population, fitness, crossover, mutation, and elitism.
- **The genotype has a first gene and subsequent modifications**, exactly as requested in the task description.

## Input File

The algorithm reads the problem instance from `ex5.json`.

The file contains:

- depot node,
- demand nodes,
- supply nodes,
- number of couriers,
- maximum operating time,
- coordinates of all nodes.

The script resolves the input path relative to `exercise5/`, so it works both when launched from the repository root and when launched from inside the `exercise5` directory.

## How to Run

From the repository root:

```bash
python3 exercise5/ex5.py
```

You can also provide a custom input file:

```bash
python3 exercise5/ex5.py --input path/to/other.json
```

## Important Note

The current implementation is structurally aligned with the task and the genotype definition, but the fitness function may still return the penalty value for all individuals on some instances if the random search does not discover a feasible route quickly enough. In other words, the algorithm is correct in form, but its search quality may need tuning for stronger optimization results.
