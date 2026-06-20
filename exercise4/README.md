# Exercise 4 - Documentation

## Overview

This program demonstrates a small genetic algorithm pipeline for bit-string chromosomes. Each individual is represented as a string of `0` and `1` characters. The program uses the number of ones in the chromosome as the fitness value.

Individuals are sorted by fitness in descending order. The best individual receives the highest rank weight, and the worst receives the lowest.

The program uses one point crossover. A random cut point is chosen between the first and last gene, and the child receives the prefix from one parent and the suffix from the other parent.

Mutation is implemented as bit flip mutation.

#
## Requirements

### Python Version
- Minimum Python 3.9

## Running the Program

By default, the program reads configuration from `ex4.json` in the same directory as the source file.

You can provide your own input file by adding its path as an execution argument:

```bash
python ex4.py path/to/file/input.json
```

Example JSON structure:

```json
{
	"population_size": 10,
	"chromosome_length": 12,
	"selection_size": 10,
	"offspring_size": 10,
	"mutation_rate": 0.05,
	"crossover_rate": 0.9,
}
```