# Exercise 3 - Documentation

## Overview

This program implements a greedy task scheduling algorithm. It reads a directed acyclic graph of tasks with data dependencies and allocates them to multiple resources while minimizing total execution cost.

#
## Requirements

### Python Version
- Minimum Python 3.9

#
## Input Data Format

You must provide input in the following JSON:

```json
{
    "tasks": [
        "T1",
        "T2",
        "T3",
        "T4"
    ],
    "dependencies": [
        {
            "source": "T1",
            "target": "T3",
            "data_size": 5
        },
        {
            "source": "T2",
            "target": "T3",
            "data_size": 3
        },
        {
            "source": "T3",
            "target": "T4",
            "data_size": 2
        }
    ],
    "resources": [
        {
            "id": "R1",
            "execution_time": {
                "T1": 5,
                "T2": 4,
                "T3": 7,
                "T4": 3
            },
            "execution_cost": {
                "T1": 10,
                "T2": 8,
                "T3": 15,
                "T4": 6
            }
        },
        {
            "id": "R2",
            "execution_time": {
                "T1": 3,
                "T2": 6,
                "T3": 4,
                "T4": 5
            },
            "execution_cost": {
                "T1": 14,
                "T2": 7,
                "T3": 10,
                "T4": 9
            }
        }
    ],
    "channels": [
        {
            "id": "C1",
            "cost_per_unit": 1.5
        },
        {
            "id": "C2",
            "cost_per_unit": 2.0
        }
    ]
}
```

### Fields Description

**tasks** - Array of task identifiers (e.g., "T1", "T2", etc.)

**dependencies** - Array of task dependencies:
- source: The task that must complete first
- target: The task that depends on source
- data_size: Volume of data transferred from source to target

**resources** - Array of computational resources (processors) with:
- id: Resource identifier
- execution_time: Dictionary mapping each task to execution time on this resource
- execution_cost: Dictionary mapping each task to execution cost on this resource

**channels** - Array of data transfer channels with:
- id: Channel identifier
- cost_per_unit: Cost per unit of data transferred

#
## Running the Program

```bash
python ex3.py
```

By default, the program looks for the input file named `task_schedule.json` in the same directory as the source file.

You can provide your own input file by adding its path as an execution argument:

```bash
python ex3.py path/to/file/input.json
```

#
## Program Output

The program prints detailed scheduling results:

```
T1   → R1  | start=   0.0 | finish=   5.0 | exec_cost=   10.0 | comm_cost=    0.0
T2   → R2  | start=   0.0 | finish=   6.0 | exec_cost=    7.0 | comm_cost=    0.0
T3   → R2  | start=   6.0 | finish=  10.0 | exec_cost=   10.0 | comm_cost=    7.5
T4   → R1  | start=  10.0 | finish=  13.0 | exec_cost=    6.0 | comm_cost=    3.0

SUMMARY
--------------------------------------------------------------------------------
Total execution time: 13.0
Total cost: 43.5
```