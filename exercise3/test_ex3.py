import json
import pytest
from ex3 import (
    Task,
    Dependency,
    Resource,
    Channel,
    ScheduledTask,
    GreedyScheduler,
    load_input_file,
)


# ── Dataclass Tests ──────────────────────────────────────────────────────────

class TestDataclasses:
    def test_task_creation(self):
        t = Task(id="T1")
        assert t.id == "T1"

    def test_dependency_creation(self):
        d = Dependency(source="T1", target="T2", data_size=5.0)
        assert d.source == "T1"
        assert d.target == "T2"
        assert d.data_size == 5.0

    def test_resource_creation(self):
        r = Resource(
            id="R1",
            execution_time={"T1": 5, "T2": 4},
            execution_cost={"T1": 10, "T2": 8},
        )
        assert r.id == "R1"
        assert r.execution_time["T1"] == 5
        assert r.execution_cost["T2"] == 8

    def test_channel_creation(self):
        c = Channel(id="C1", cost_per_unit=1.5)
        assert c.id == "C1"
        assert c.cost_per_unit == 1.5

    def test_scheduled_task_creation(self):
        s = ScheduledTask(
            task_id="T1",
            resource_id="R1",
            start_time=0.0,
            finish_time=5.0,
            execution_cost=10.0,
            communication_cost=0.0,
        )
        assert s.task_id == "T1"
        assert s.resource_id == "R1"
        assert s.start_time == 0.0
        assert s.finish_time == 5.0
        assert s.execution_cost == 10.0
        assert s.communication_cost == 0.0


# ── Topological Sort Tests ──────────────────────────────────────────────────

class TestTopologicalSort:
    def test_simple_chain(self):
        tasks = [Task("T1"), Task("T2"), Task("T3")]
        deps = [Dependency("T1", "T2", 1), Dependency("T2", "T3", 1)]
        resources = [Resource("R1", {"T1": 1, "T2": 1, "T3": 1}, {"T1": 1, "T2": 1, "T3": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        order = scheduler.topological_sort()
        assert order == ["T1", "T2", "T3"]

    def test_multiple_roots(self):
        tasks = [Task("T1"), Task("T2"), Task("T3")]
        deps = [Dependency("T1", "T3", 1), Dependency("T2", "T3", 1)]
        resources = [Resource("R1", {"T1": 1, "T2": 1, "T3": 1}, {"T1": 1, "T2": 1, "T3": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        order = scheduler.topological_sort()
        assert order.index("T1") < order.index("T3")
        assert order.index("T2") < order.index("T3")

    def test_no_dependencies(self):
        tasks = [Task("T1"), Task("T2")]
        deps = []
        resources = [Resource("R1", {"T1": 1, "T2": 1}, {"T1": 1, "T2": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        order = scheduler.topological_sort()
        assert set(order) == {"T1", "T2"}

    def test_single_task(self):
        tasks = [Task("T1")]
        deps = []
        resources = [Resource("R1", {"T1": 1}, {"T1": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        assert scheduler.topological_sort() == ["T1"]

    def test_cycle_detection(self):
        tasks = [Task("T1"), Task("T2"), Task("T3")]
        deps = [
            Dependency("T1", "T2", 1),
            Dependency("T2", "T3", 1),
            Dependency("T3", "T1", 1),
        ]
        resources = [Resource("R1", {"T1": 1, "T2": 1, "T3": 1}, {"T1": 1, "T2": 1, "T3": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        with pytest.raises(ValueError, match="Graph has a cycle"):
            scheduler.topological_sort()

    def test_self_loop(self):
        tasks = [Task("T1")]
        deps = [Dependency("T1", "T1", 1)]
        resources = [Resource("R1", {"T1": 1}, {"T1": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        with pytest.raises(ValueError, match="Graph has a cycle"):
            scheduler.topological_sort()

    def test_diamond_dag(self):
        tasks = [Task("T1"), Task("T2"), Task("T3"), Task("T4")]
        deps = [
            Dependency("T1", "T2", 1),
            Dependency("T1", "T3", 1),
            Dependency("T2", "T4", 1),
            Dependency("T3", "T4", 1),
        ]
        resources = [Resource("R1", {t.id: 1 for t in tasks}, {t.id: 1 for t in tasks})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        order = scheduler.topological_sort()
        assert order[0] == "T1"
        assert order[-1] == "T4"


# ── Scheduling Tests ────────────────────────────────────────────────────────

class TestSchedule:
    def test_known_example_output(self):
        """Verify against the documented example in README/ALGORITHM.md."""
        tasks = [Task("T1"), Task("T2"), Task("T3"), Task("T4")]
        deps = [
            Dependency("T1", "T3", 5),
            Dependency("T2", "T3", 3),
            Dependency("T3", "T4", 2),
        ]
        resources = [
            Resource("R1", {"T1": 5, "T2": 4, "T3": 7, "T4": 3}, {"T1": 10, "T2": 8, "T3": 15, "T4": 6}),
            Resource("R2", {"T1": 3, "T2": 6, "T3": 4, "T4": 5}, {"T1": 14, "T2": 7, "T3": 10, "T4": 9}),
        ]
        channels = [Channel("C1", 1.5), Channel("C2", 2.0)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()

        assert total_time == 13.0
        assert total_cost == 43.5

        # T1 → R1, [0, 5], cost=10
        t1 = schedule["T1"]
        assert t1.resource_id == "R1"
        assert t1.start_time == 0.0
        assert t1.finish_time == 5.0
        assert t1.execution_cost == 10.0
        assert t1.communication_cost == 0.0

        # T2 → R2, [0, 6], cost=7
        t2 = schedule["T2"]
        assert t2.resource_id == "R2"
        assert t2.start_time == 0.0
        assert t2.finish_time == 6.0
        assert t2.execution_cost == 7.0
        assert t2.communication_cost == 0.0

        # T3 → R2, [6, 10], cost=17.5 (10 exec + 7.5 comm)
        t3 = schedule["T3"]
        assert t3.resource_id == "R2"
        assert t3.start_time == 6.0
        assert t3.finish_time == 10.0
        assert t3.execution_cost == 10.0
        assert t3.communication_cost == 7.5

        # T4 tie: R1=[10,13] cost=9, R2=[10,15] cost=9. R1 wins (first encountered).
        t4 = schedule["T4"]
        assert t4.resource_id == "R1"
        assert t4.start_time == 10.0
        assert t4.finish_time == 13.0
        assert t4.execution_cost == 6.0
        assert t4.communication_cost == 3.0

    def test_single_task_single_resource(self):
        tasks = [Task("T1")]
        resources = [Resource("R1", {"T1": 5}, {"T1": 10})]
        channels = [Channel("C1", 1.0)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()
        assert schedule["T1"].resource_id == "R1"
        assert schedule["T1"].start_time == 0.0
        assert schedule["T1"].finish_time == 5.0
        assert total_time == 5.0
        assert total_cost == 10.0

    def test_two_independent_tasks(self):
        """Independent tasks should run in parallel on different resources."""
        tasks = [Task("T1"), Task("T2")]
        resources = [
            Resource("R1", {"T1": 2, "T2": 100}, {"T1": 1, "T2": 100}),
            Resource("R2", {"T1": 100, "T2": 3}, {"T1": 100, "T2": 1}),
        ]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()
        assert schedule["T1"].resource_id == "R1"
        assert schedule["T2"].resource_id == "R2"
        assert schedule["T1"].start_time == 0.0
        assert schedule["T1"].finish_time == 2.0
        assert schedule["T2"].start_time == 0.0
        assert schedule["T2"].finish_time == 3.0
        assert total_time == 3.0

    def test_resource_blocking(self):
        """Tasks on same resource must wait for resource to be free."""
        tasks = [Task("T1"), Task("T2")]
        resources = [Resource("R1", {"T1": 5, "T2": 5}, {"T1": 10, "T2": 10})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        schedule, total_time, _ = scheduler.schedule()
        assert schedule["T1"].start_time == 0.0
        assert schedule["T1"].finish_time == 5.0
        assert schedule["T2"].start_time == 5.0
        assert schedule["T2"].finish_time == 10.0
        assert total_time == 10.0

    def test_cheapest_channel_used(self):
        """Communication cost should use cheapest channel."""
        tasks = [Task("T1"), Task("T2")]
        deps = [Dependency("T1", "T2", 10)]
        resources = [
            Resource("R1", {"T1": 1, "T2": 1}, {"T1": 1, "T2": 1}),
            Resource("R2", {"T1": 100, "T2": 1}, {"T1": 100, "T2": 1}),
        ]
        channels = [Channel("C1", 100.0), Channel("C2", 1.0)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, _, total_cost = scheduler.schedule()
        # T1 → R1 (cheaper), T2 → R1 (no comm cost) or T2 → R2 (comm cost 10*1=10)
        # T1 on R1, T2 on R1: comm=0, exec=1+1=2, total=2
        # T1 on R1, T2 on R2: comm=10*1=10, exec=1+1=2, total=12
        # So T2 should be on R1 to minimize cost
        assert schedule["T1"].resource_id == "R1"
        assert schedule["T2"].resource_id == "R1"
        assert total_cost == 2.0

    def test_same_resource_no_communication_cost(self):
        """No communication cost when tasks on same resource."""
        tasks = [Task("T1"), Task("T2")]
        deps = [Dependency("T1", "T2", 100)]
        resources = [Resource("R1", {"T1": 1, "T2": 1}, {"T1": 1, "T2": 1})]
        channels = [Channel("C1", 999.0)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, _, total_cost = scheduler.schedule()
        assert schedule["T1"].communication_cost == 0.0
        assert schedule["T2"].communication_cost == 0.0
        assert total_cost == 2.0

    def test_different_resource_communication_cost(self):
        """Communication cost incurred when tasks on different resources."""
        tasks = [Task("T1"), Task("T2")]
        deps = [Dependency("T1", "T2", 10)]
        resources = [
            Resource("R1", {"T1": 1, "T2": 1}, {"T1": 1, "T2": 999}),
            Resource("R2", {"T1": 999, "T2": 1}, {"T1": 999, "T2": 1}),
        ]
        channels = [Channel("C1", 2.0)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, _, total_cost = scheduler.schedule()
        # T1 → R1 (cost 1), T2 → R2 (cost 1, but comm cost 10*2=20) → total=22
        # T1 → R1, T2 → R1 (cost 999) → total=1000
        # So T2 → R2 with comm cost
        assert schedule["T1"].resource_id == "R1"
        assert schedule["T2"].resource_id == "R2"
        assert schedule["T2"].communication_cost == 20.0
        assert total_cost == 22.0

    def test_deterministic_output(self):
        """Same input always produces same schedule."""
        tasks = [Task("T1"), Task("T2"), Task("T3")]
        deps = [Dependency("T1", "T3", 5), Dependency("T2", "T3", 3)]
        resources = [
            Resource("R1", {"T1": 5, "T2": 4, "T3": 7}, {"T1": 10, "T2": 8, "T3": 15}),
            Resource("R2", {"T1": 3, "T2": 6, "T3": 4}, {"T1": 14, "T2": 7, "T3": 10}),
        ]
        channels = [Channel("C1", 1.5)]
        s1 = GreedyScheduler(tasks, deps, resources, channels).schedule()
        s2 = GreedyScheduler(tasks, deps, resources, channels).schedule()
        _, t1, c1 = s1
        _, t2, c2 = s2
        assert t1 == t2
        assert c1 == c2

    def test_cost_minimization_respected(self):
        """Verify scheduler picks cheaper option even if slower."""
        tasks = [Task("T1")]
        resources = [
            Resource("R1", {"T1": 100}, {"T1": 1}),   # slow, cheap
            Resource("R2", {"T1": 1}, {"T1": 1000}),   # fast, expensive
        ]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()
        assert schedule["T1"].resource_id == "R1"
        assert total_time == 100.0
        assert total_cost == 1.0

    def test_no_resources(self):
        tasks = [Task("T1")]
        with pytest.raises(AttributeError):
            GreedyScheduler(tasks, [], [], [Channel("C1", 1)]).schedule()

    def test_missing_task_in_resource(self):
        """Task exists but not in resource execution_time — should KeyError."""
        tasks = [Task("T1"), Task("T2")]
        resources = [Resource("R1", {"T1": 1}, {"T1": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        with pytest.raises(KeyError):
            scheduler.schedule()

    def test_multiple_parents_ready_time(self):
        """Task must wait for latest parent to finish."""
        tasks = [Task("T1"), Task("T2"), Task("T3")]
        deps = [Dependency("T1", "T3", 1), Dependency("T2", "T3", 1)]
        resources = [
            Resource("R1", {"T1": 10, "T2": 100, "T3": 1}, {"T1": 1, "T2": 100, "T3": 1}),
            Resource("R2", {"T1": 100, "T2": 5, "T3": 1}, {"T1": 100, "T2": 1, "T3": 1}),
        ]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, _, _ = scheduler.schedule()
        # T1 → R1 (cheap, finish 10), T2 → R2 (cheap, finish 5)
        # T3 ready_time = max(10, 5) = 10
        assert schedule["T3"].start_time >= 10.0

    def test_deep_chain(self):
        """Linear chain of many tasks."""
        n = 10
        tasks = [Task(f"T{i}") for i in range(n)]
        deps = [Dependency(f"T{i}", f"T{i+1}", 1) for i in range(n - 1)]
        resources = [Resource("R1", {f"T{i}": 1 for i in range(n)}, {f"T{i}": 1 for i in range(n)})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        _, total_time, total_cost = scheduler.schedule()
        assert total_time == float(n)
        assert total_cost == float(n)

    def test_empty_tasks(self):
        scheduler = GreedyScheduler([], [], [Resource("R1", {}, {})], [Channel("C1", 1)])
        schedule, total_time, total_cost = scheduler.schedule()
        assert schedule == {}
        assert total_time == 0.0
        assert total_cost == 0.0


# ── Load Input File Tests ───────────────────────────────────────────────────

class TestLoadInputFile:
    def test_load_valid_file(self, tmp_path):
        data = {
            "tasks": ["T1", "T2"],
            "dependencies": [{"source": "T1", "target": "T2", "data_size": 5}],
            "resources": [
                {
                    "id": "R1",
                    "execution_time": {"T1": 5, "T2": 4},
                    "execution_cost": {"T1": 10, "T2": 8},
                }
            ],
            "channels": [{"id": "C1", "cost_per_unit": 1.5}],
        }
        filepath = tmp_path / "input.json"
        filepath.write_text(json.dumps(data))
        tasks, deps, resources, channels = load_input_file(str(filepath))
        assert len(tasks) == 2
        assert tasks[0].id == "T1"
        assert len(deps) == 1
        assert deps[0].source == "T1"
        assert deps[0].data_size == 5
        assert len(resources) == 1
        assert resources[0].id == "R1"
        assert resources[0].execution_time["T2"] == 4
        assert len(channels) == 1
        assert channels[0].cost_per_unit == 1.5

    def test_load_empty_structures(self, tmp_path):
        data = {"tasks": [], "dependencies": [], "resources": [], "channels": []}
        filepath = tmp_path / "empty.json"
        filepath.write_text(json.dumps(data))
        tasks, deps, resources, channels = load_input_file(str(filepath))
        assert tasks == []
        assert deps == []
        assert resources == []
        assert channels == []

    def test_load_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_input_file("/nonexistent/path.json")

    def test_load_invalid_json(self, tmp_path):
        filepath = tmp_path / "bad.json"
        filepath.write_text("{invalid json}")
        with pytest.raises(json.JSONDecodeError):
            load_input_file(str(filepath))


# ── Integration Tests ───────────────────────────────────────────────────────

class TestIntegration:
    def test_default_input_file(self):
        script_dir = __file__.rsplit("/", 1)[0]
        filepath = f"{script_dir}/task_schedule.json"
        tasks, deps, resources, channels = load_input_file(filepath)
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()
        assert len(schedule) == 4
        assert total_time == 13.0
        assert total_cost == 43.5

    def test_schedule_invariants(self):
        """Post-conditions every schedule must satisfy."""
        tasks = [Task("T1"), Task("T2"), Task("T3"), Task("T4")]
        deps = [
            Dependency("T1", "T3", 5),
            Dependency("T2", "T3", 3),
            Dependency("T3", "T4", 2),
        ]
        resources = [
            Resource("R1", {"T1": 5, "T2": 4, "T3": 7, "T4": 3}, {"T1": 10, "T2": 8, "T3": 15, "T4": 6}),
            Resource("R2", {"T1": 3, "T2": 6, "T3": 4, "T4": 5}, {"T1": 14, "T2": 7, "T3": 10, "T4": 9}),
        ]
        channels = [Channel("C1", 1.5)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        schedule, total_time, total_cost = scheduler.schedule()

        # All tasks scheduled
        assert set(schedule.keys()) == {"T1", "T2", "T3", "T4"}

        for task_id, st in schedule.items():
            # Non-negative times
            assert st.start_time >= 0
            assert st.finish_time > st.start_time or st.start_time == 0.0
            assert st.finish_time >= st.start_time
            # Resource assigned
            assert st.resource_id in ("R1", "R2")
            # Non-negative costs
            assert st.execution_cost >= 0
            assert st.communication_cost >= 0

        # Total time is max finish time
        assert total_time == max(st.finish_time for st in schedule.values())

        # Total cost is sum of exec + comm
        expected_total = sum(st.execution_cost + st.communication_cost for st in schedule.values())
        assert total_cost == expected_total

        # Precedence constraints respected
        for dep in deps:
            parent = schedule[dep.source]
            child = schedule[dep.target]
            assert child.start_time >= parent.finish_time

        # No resource overlaps
        resource_timeline = {r.id: [] for r in resources}
        for st in schedule.values():
            resource_timeline[st.resource_id].append((st.start_time, st.finish_time))
        for r_id, intervals in resource_timeline.items():
            intervals.sort()
            for i in range(len(intervals) - 1):
                assert intervals[i][1] <= intervals[i + 1][0], (
                    f"Overlap on {r_id}: {intervals[i]} -> {intervals[i+1]}"
                )


class TestEdgeCases:
    def test_duplicate_task_id_raises_error(self):
        tasks = [Task("T1"), Task("T1")]
        resources = [Resource("R1", {"T1": 1}, {"T1": 1})]
        channels = [Channel("C1", 1)]
        scheduler = GreedyScheduler(tasks, [], resources, channels)
        with pytest.raises(ValueError, match="Graph has a cycle"):
            scheduler.topological_sort()

    def test_large_data_transfer(self):
        tasks = [Task("T1"), Task("T2")]
        deps = [Dependency("T1", "T2", 1e6)]
        resources = [
            Resource("R1", {"T1": 1, "T2": 1}, {"T1": 1, "T2": 999999}),
            Resource("R2", {"T1": 999999, "T2": 1}, {"T1": 999999, "T2": 1}),
        ]
        channels = [Channel("C1", 1.0)]
        scheduler = GreedyScheduler(tasks, deps, resources, channels)
        _, _, total_cost = scheduler.schedule()
        # T1→R1, T2→R2: 1 + 1 + 1e6 = 1000002
        # T1→R1, T2→R1: 1 + 999999 = 1000000
        assert total_cost == 1000000.0
