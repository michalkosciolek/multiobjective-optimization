# Exercise 5 - documentation

## Overview

This program uses a genetic algorithm to assign demand nodes to couriers. Every demand node must be visited exactly once, while supply nodes can be used when a courier needs to refuel.

The program keeps a base assignment of demand nodes to couriers and then applies route modifications such as moving or swapping nodes. Fitness is based on total travel distance, and infeasible solutions receive a large penalty.

#
## Requirements

### Python Version
- Minimum Python 3.9

#
## Input data format

You have to provide input file in JSON format with the following structure:

```json
{
	"depot": 0,
	"demand_nodes": [1, 2, 3, 4],
	"supply_nodes": [0, 5],
	"num_couriers": 2,
	"max_operating_time": 90,
	"coords": {
		"0": [50, 50],
		"1": [10, 20],
		"2": [15, 80],
		"3": [40, 90],
		"4": [80, 20],
		"5": [20, 50]
	}
}
```

### Fields Description

**depot** - Starting and ending node for every courier.

**demand_nodes** - Nodes that must be assigned to couriers.

**supply_nodes** - Nodes that can be used for refueling.

**num_couriers** - Number of available couriers.

**max_operating_time** - Maximum distance a courier can travel before refueling.

**coords** - Node coordinates used to calculate Euclidean distance.

#
## Running the Program

```bash
python3 exercise5/ex5.py
```

By default, the program reads the input file named `ex5.json` from the same directory as the source file.

You can provide your own input file by adding the `--input` argument:

```bash
python3 exercise5/ex5.py --input path/to/file/input.json
```

#
## Program Output

The program prints the best courier allocation found by the genetic algorithm, for example:

```text
Gen 0 | Best Cost: 123.45
Gen 20 | Best Cost: 98.10

ALLOCATION FOUND
Courier 0: Visits Demand Nodes [1, 4]
Courier 1: Visits Demand Nodes [2, 3]
```
