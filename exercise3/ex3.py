from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
import json
import sys
import os


@dataclass
class Task:
    id: str


@dataclass
class Dependency:
    source: str
    target: str
    data_size: float


@dataclass
class Resource:
    id: str
    execution_time: Dict[str, float]
    execution_cost: Dict[str, float]


@dataclass
class Channel:
    id: str
    cost_per_unit: float


@dataclass
class ScheduledTask:
    task_id: str
    resource_id: str
    start_time: float
    finish_time: float
    execution_cost: float
    communication_cost: float


class GreedyScheduler:

    def __init__(
        self,
        tasks: List[Task],
        dependencies: List[Dependency],
        resources: List[Resource],
        channels: List[Channel],
    ):
        self.tasks = tasks
        self.dependencies = dependencies
        self.resources = resources
        self.channels = channels

        self.task_map = {t.id: t for t in tasks}
        self.resource_map = {r.id: r for r in resources}

        self.parents = defaultdict(list)
        self.children = defaultdict(list)

        for dep in dependencies:
            self.parents[dep.target].append(dep)
            self.children[dep.source].append(dep)

    def topological_sort(self) -> List[str]:
        indegree = {task.id: 0 for task in self.tasks}

        for dep in self.dependencies:
            indegree[dep.target] += 1

        queue = deque()

        for task_id, deg in indegree.items():
            if deg == 0:
                queue.append(task_id)

        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for dep in self.children[current]:
                indegree[dep.target] -= 1

                if indegree[dep.target] == 0:
                    queue.append(dep.target)

        if len(order) != len(self.tasks):
            raise ValueError("Graph has a cycle")

        return order

    def schedule(self):

        order = self.topological_sort()

        resource_available_time = {resource.id: 0.0 for resource in self.resources}

        task_schedule: Dict[str, ScheduledTask] = {}

        total_cost = 0.0
        total_time = 0.0

        cheapest_channel = min(self.channels, key=lambda c: c.cost_per_unit)

        for task_id in order:

            best_resource = None
            best_metric = float("inf")

            best_start = 0.0
            best_finish = 0.0
            best_exec_cost = 0.0
            best_comm_cost = 0.0

            for resource in self.resources:

                execution_time = resource.execution_time[task_id]
                execution_cost = resource.execution_cost[task_id]

                ready_time = resource_available_time[resource.id]

                communication_cost = 0.0

                for dep in self.parents[task_id]:

                    parent_schedule = task_schedule[dep.source]

                    ready_time = max(ready_time, parent_schedule.finish_time)

                    if parent_schedule.resource_id != resource.id:
                        communication_cost += (
                            dep.data_size * cheapest_channel.cost_per_unit
                        )

                start_time = ready_time
                finish_time = start_time + execution_time

                metric = execution_cost + communication_cost

                if metric < best_metric:
                    best_metric = metric

                    best_resource = resource

                    best_start = start_time
                    best_finish = finish_time
                    best_exec_cost = execution_cost
                    best_comm_cost = communication_cost

            scheduled = ScheduledTask(
                task_id=task_id,
                resource_id=best_resource.id,
                start_time=best_start,
                finish_time=best_finish,
                execution_cost=best_exec_cost,
                communication_cost=best_comm_cost,
            )

            task_schedule[task_id] = scheduled

            resource_available_time[best_resource.id] = best_finish

            total_cost += best_exec_cost + best_comm_cost
            total_time = max(total_time, best_finish)

        return task_schedule, total_time, total_cost


def load_input_file(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)

    tasks = [Task(id=t) for t in data["tasks"]]

    dependencies = [
        Dependency(
            source=dep["source"], target=dep["target"], data_size=dep["data_size"]
        )
        for dep in data["dependencies"]
    ]

    resources = [
        Resource(
            id=r["id"],
            execution_time=r["execution_time"],
            execution_cost=r["execution_cost"],
        )
        for r in data["resources"]
    ]

    channels = [
        Channel(id=c["id"], cost_per_unit=c["cost_per_unit"]) for c in data["channels"]
    ]

    return tasks, dependencies, resources, channels


def get_input_filepath() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "task_schedule.json")


def print_schedule_results(
    schedule: Dict[str, ScheduledTask], total_time: float, total_cost: float
):
    sorted_schedule = sorted(schedule.items(), key=lambda x: (x[1].start_time, x[0]))

    for task_id, result in sorted_schedule:
        print(
            f"{task_id:4} → {result.resource_id:3} | "
            f"start={result.start_time:6.1f} | "
            f"finish={result.finish_time:6.1f} | "
            f"exec_cost={result.execution_cost:7.1f} | "
            f"comm_cost={result.communication_cost:7.1f}"
        )

    print("\nSUMMARY")
    print("-" * 80)
    print(f"Total execution time: {total_time:.1f}")
    print(f"Total cost: {total_cost:.1f}")


if __name__ == "__main__":

    input_file = get_input_filepath()

    tasks, dependencies, resources, channels = load_input_file(input_file)

    scheduler = GreedyScheduler(tasks, dependencies, resources, channels)
    schedule, total_time, total_cost = scheduler.schedule()

    print_schedule_results(schedule, total_time, total_cost)
