# Task Scheduling for Heterogeneous Computing Environments - Algorithm Documentation

## Overview

This algorithm implements a **greedy task scheduling approach** for parallel computing environments. It takes a directed acyclic graph (DAG) of tasks with data dependencies and allocates them to heterogeneous resources (processors) while minimizing total cost. The algorithm considers task dependencies, resource availability, and inter-resource communication costs.

---

## Problem Description

**Input:**
- A DAG of tasks with precedence constraints
- Multiple heterogeneous resources (processors) with different capabilities
- Task execution times and costs vary per resource
- Communication channels for data transfer between resources
- Data dependencies with transfer sizes

**Output:**
- Task-to-resource assignment
- Execution schedule with start/finish times
- Per-task execution and communication costs
- Total cost of the schedule

**Objective:** Minimize total cost using a greedy rule:
- For each task and candidate resource, compute `execution_cost + communication_cost`
- Select the resource with the lowest total cost
- Ties are resolved by the first resource encountered

---

## Data Models (Dataclasses)

### 1. `Task`
```python
@dataclass
class Task:
    id: str
```

**Purpose:** Represents a computational task in the workflow.

**Fields:**
- `id` (str): Unique identifier for the task (e.g., "T1", "T2")

**Usage:** Serves as the basic unit of computation that needs to be scheduled on resources.

---

### 2. `Dependency`
```python
@dataclass
class Dependency:
    source: str      # ID of the source task
    target: str      # ID of the target task
    data_size: float # Size of data transferred
```

**Purpose:** Represents a data dependency between two tasks. Task scheduling must respect these precedence constraints.

**Fields:**
- `source`: ID of the task that must complete first
- `target`: ID of the task that depends on the source
- `data_size`: Volume of data transferred from source to target (in units)

**Usage:** When task A depends on task B:
- Task A cannot start until task B finishes
- If A and B run on different resources, communication cost applies: `data_size × channel_cost_per_unit`

**Example:** 
```python
Dependency("T1", "T3", 5)  # T3 depends on T1, 5 units of data transferred
```

---

### 3. `Resource`
```python
@dataclass
class Resource:
    id: str
    execution_time: Dict[str, float]    # Task ID -> execution time
    execution_cost: Dict[str, float]    # Task ID -> execution cost
```

**Purpose:** Represents a computational resource (processor/machine) with specific capabilities.

**Fields:**
- `id`: Unique identifier (e.g., "R1", "R2")
- `execution_time`: Dictionary mapping each task to how long it takes on this resource
- `execution_cost`: Dictionary mapping each task to the monetary cost on this resource

**Usage:** Resources are heterogeneous—each has different performance characteristics. The scheduler selects the best resource for each task using the greedy total-cost rule.

**Example:**
```python
Resource(
    id="R1",
    execution_time={"T1": 5, "T2": 4, "T3": 7},
    execution_cost={"T1": 10, "T2": 8, "T3": 15}
)
```

---

### 4. `Channel`
```python
@dataclass
class Channel:
    id: str
    cost_per_unit: float
```

**Purpose:** Represents a communication channel for data transfer between resources.

**Fields:**
- `id`: Identifier (e.g., "C1", "C2")
- `cost_per_unit`: Cost per unit of data transferred

**Usage:** When tasks on different resources communicate, the communication cost is calculated as:
```
communication_cost = data_size × cost_per_unit
```

The algorithm automatically selects the cheapest channel to minimize cost.

---

### 5. `ScheduledTask`
```python
@dataclass
class ScheduledTask:
    task_id: str
    resource_id: str
    start_time: float
    finish_time: float
    execution_cost: float
    communication_cost: float
```

**Purpose:** Represents the result of scheduling—where and when a task is executed.

**Fields:**
- `task_id`: The task being scheduled
- `resource_id`: Which resource executes it
- `start_time`: When execution begins
- `finish_time`: When execution completes
- `execution_cost`: Cost of executing the task on the assigned resource
- `communication_cost`: Cost of transferring data from parent tasks on other resources

**Usage:** Output of the scheduling process; provides the complete execution plan.

---

## Algorithm Description

### GreedyScheduler Class

The core scheduling algorithm is implemented in the `GreedyScheduler` class.

#### Initialization

```python
def __init__(self, tasks, dependencies, resources, channels):
```

**Purpose:** Set up the scheduler with problem data and build internal data structures.

**Key Structures Built:**
- `self.parents[task_id]`: List of dependencies where this task is the target (incoming edges)
- `self.children[task_id]`: List of dependencies where this task is the source (outgoing edges)

These enable fast lookup of parent/child relationships needed during scheduling.

---

#### Step 1: Topological Sort

```python
def topological_sort(self) -> List[str]:
```

**Purpose:** Determine a valid execution order that respects all dependencies.

**Algorithm (Kahn's Algorithm):**
1. Calculate in-degree (number of incoming edges) for each task
2. Add all tasks with in-degree 0 (no dependencies) to a queue
3. Process queue:
   - Remove a task from the queue
   - Decrease in-degree of all dependent tasks
   - If any dependent task's in-degree becomes 0, add it to the queue
4. Return the processing order

**Why:** We must schedule tasks in topological order to ensure parent tasks are scheduled before their children.

**Complexity:** O(V + E) where V = number of tasks, E = number of dependencies.

**Example with our test case:**
- Tasks: T1, T2, T3, T4
- Dependencies: T1→T3, T2→T3, T3→T4
- Result order: [T1, T2, T3, T4] or [T2, T1, T3, T4] (both valid)

---

#### Step 2: Greedy Scheduling

```python
def schedule(self):
```

**Purpose:** Assign each task to the best resource, processing in topological order.

**Algorithm:**

For each task in topological order:

1. **Initialize tracking tables:**
   - `resource_available_time`: When each resource becomes free
   - `task_schedule`: Results for already-scheduled tasks

2. **For each task, evaluate all resources:**
   - Calculate execution time on this resource
   - Calculate ready time:
     - Resource must be free: `resource_available_time[resource]`
     - All parents must finish: `max(parent.finish_time for each parent)`
     - `ready_time = max(resource_free_time, latest_parent_finish_time)`
   
   - Calculate start and finish times:
     - `start_time = ready_time`
     - `finish_time = start_time + execution_time`
   
   - Calculate communication cost (always calculated):
     - For each parent task:
       - If parent on same resource: no communication cost
       - If parent on different resource: `communication_cost += data_size × cheapest_channel.cost_per_unit`
   
   - Calculate total cost: `execution_cost + communication_cost`

3. **Greedy Selection:**
   - Select the resource with **minimum total cost**
   - Total cost is `execution_cost + communication_cost`
   - Ties keep the first resource encountered in the loop
   - Record: best_resource, best_start, best_finish, best_exec_cost, best_comm_cost

4. **Update state:**
   - Store the resulting `ScheduledTask`
   - Update resource availability: `resource_available_time[resource] = finish_time`
   - Accumulate total cost and track maximum finish time (makespan)

5. **Return results:** `(schedule_dict, total_time, total_cost)`

**Key Insight:** Communication costs are always calculated, reported, and included in the resource comparison. The scheduler does not have a separate time-optimization mode.

---

## Example Walkthrough

### Input Configuration

```
Tasks: T1, T2, T3 (T4 added for dependency chain)

Dependencies:
  T1 → T3 (5 units data)
  T2 → T3 (3 units data)
  T3 → T4 (2 units data)

Resources:
  R1: exec_time={T1:5, T2:4, T3:7, T4:3}, exec_cost={T1:10, T2:8, T3:15, T4:6}
  R2: exec_time={T1:3, T2:6, T3:4, T4:5}, exec_cost={T1:14, T2:7, T3:10, T4:9}

Channels:
  C1: cost_per_unit=1.5 (cheapest)
  C2: cost_per_unit=2.0

Optimization: greedy total-cost selection
```

### Execution Trace

#### Step 1: Topological Sort
- Initial in-degrees: T1=0, T2=0, T3=2, T4=1
- Queue: [T1, T2]
- Process T1: T3 in-degree → 1
- Process T2: T3 in-degree → 0, add T3
- Process T3: T4 in-degree → 0, add T4
- Process T4: done
- Order: **[T1, T2, T3, T4]**

#### Step 2: Schedule Task T1

**No parents, no communication cost.**

| Resource | Exec Time | Exec Cost | Ready | Start | Finish | Total Cost |
|----------|-----------|-----------|-------|-------|--------|-----------|
| R1       | 5         | 10        | 0     | 0     | 5      | 10        |
| R2       | 3         | 14        | 0     | 0     | 3      | 14        |

**Select R1** (lower cost: 10 < 14)

**Result:** T1 → R1, [0, 5], cost=10

```
Resource availability: R1=5, R2=0
```

#### Step 3: Schedule Task T2

**No parents, runs independently.**

| Resource | Exec Time | Exec Cost | Ready | Start | Finish | Total Cost |
|----------|-----------|-----------|-------|-------|--------|-----------|
| R1       | 4         | 8         | 5     | 5     | 9      | 8         |
| R2       | 6         | 7         | 0     | 0     | 6      | 7         |

**Select R2** (lower cost: 7 < 8)

**Result:** T2 → R2, [0, 6], cost=7

```
Resource availability: R1=5, R2=6
```

#### Step 4: Schedule Task T3

**Parents: T1 (on R1, finishes at 5), T2 (on R2, finishes at 6)**

Communication costs:
- From T1 on R1:
  - To R1: 0 (same resource)
  - To R2: 5 × 1.5 = **7.5**
- From T2 on R2:
  - To R1: 3 × 1.5 = **4.5** (wait for R1 to be free)
  - To R2: 0 (same resource)

| Resource | Exec Time | Exec Cost | Ready | Comm Cost | Start | Finish | Total Cost |
|----------|-----------|-----------|-------|-----------|-------|--------|-----------|
| R1       | 7         | 15        | 6     | 4.5       | 6     | 13     | **19.5**  |
| R2       | 4         | 10        | 6     | 7.5       | 6     | 10     | **17.5**  |

**Select R2** (lower cost: 17.5 < 19.5)

**Result:** T3 → R2, [6, 10], cost=17.5

```
Resource availability: R1=5, R2=10
```

#### Step 5: Schedule Task T4

**Parent: T3 (on R2, finishes at 10)**

Communication costs:
- From T3 on R2:
  - To R1: 2 × 1.5 = **3** (wait for R1 to be free)
  - To R2: 0 (same resource)

| Resource | Exec Time | Exec Cost | Ready | Comm Cost | Start | Finish | Total Cost |
|----------|-----------|-----------|-------|-----------|-------|--------|-----------|
| R1       | 3         | 6         | 10    | 3         | 10    | 13     | **9**     |
| R2       | 5         | 9         | 10    | 0         | 10    | 15     | **9**     |

Both equal! Select **R1** (first match)

**Result:** T4 → R1, [10, 13], cost=9

### Final Schedule

```
Task  Resource  Start  Finish  Cost
─────────────────────────────────
T1    R1        0      5       10
T2    R2        0      6       7
T3    R2        6      10      17.5
T4    R1        10     13      9

Total execution time: 13
Total cost: 43.5
```

**Communication details:**
- T1→T3: R1→R2, 5 units @ 1.5 = 7.5
- T2→T3: R2→R2, no communication
- T3→T4: R2→R1, 2 units @ 1.5 = 3

---

## Algorithm Properties

### Time Complexity
- Topological sorting: **O(V + E)**
- Scheduling loop: **O(V × M × P)** where:
  - V = number of tasks
  - M = number of resources
  - P = average parents per task
- **Overall: O(V × M × P)**

### Space Complexity
- **O(V + E + M)** for storing tasks, dependencies, resources, and intermediate data

### Optimality
- **Not optimal!** Greedy algorithms don't guarantee global optimum
- Makes locally optimal choices (minimize time or cost for current task)
- May lead to suboptimal schedules due to early decisions blocking better future choices

### Why Greedy Works Here
1. Simple and fast (polynomial time)
2. Good quality solutions for practical problem sizes
3. Scales well with large task graphs
4. Can be enhanced with local search or other heuristics

### Greedy Policy

The current implementation uses a single greedy policy:
- Select the resource with minimum `execution_cost + communication_cost`
- Communication cost is based on the cheapest channel only
- Start time is constrained by both resource availability and parent finish times

---

## Visualization of Example

```
TASK GRAPH:
    T1 (5 units data)
     ↓
    T3 (2 units data) ← T2 (3 units data)
     ↓
    T4

RESOURCE ALLOCATION TIMELINE:

R1: [T1____]
    0      5

R2: [T2___][T3______][T4_____]
    0     6         10       15

EXECUTION WITHOUT COMMUNICATION:
Time  R1        R2
────  ────      ────
0-5   T1
0-6           T2
6-10          T3
10-15         T4
```

---

## Key Design Decisions

1. **Greedy Strategy:** Process tasks in topological order, select best resource for each task
2. **Ready Time Calculation:** Considers both resource availability and parent task completion
3. **Communication Cost:** Only charged when tasks on different resources communicate
4. **Cheapest Channel:** Always use the lowest-cost channel for inter-resource communication
5. **Single Policy:** Focuses on minimizing total cost (execution + communication)

---

## Potential Improvements

1. **Multiple Heuristics:** Try different ordering strategies (critical path, etc.)
2. **Local Search:** After greedy solution, try task migration to nearby resources
3. **Parametric Analysis:** Vary cost weights to find Pareto-optimal solutions
4. **Dynamic Programming:** For small task graphs, compute optimal solution
5. **Genetic Algorithm:** For large instances, use metaheuristics
6. **Heterogeneous Objectives:** Trade-off between cost and execution time

