import json
import subprocess
import requests
import logging
import time
from typing import Dict, Any, List, Callable, Literal, Optional
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowEngine:
    def __init__(self, workflow_definition: Dict[str, Any]):
        # ... (Initialization as before, but with stricter validation of definition)
        self._validate_workflow_definition(workflow_definition)
        self.tasks: Dict[str, "MissionCriticalTask"] = {}
        self.workflow_data: Dict[str, Any] = {}
        self.execution_status: TaskStatus = TaskStatus.PENDING
        self.task_results: Dict[str, TaskResult] = {}

    def _validate_workflow_definition(self, definition: Dict[str, Any]):
        # Implement rigorous schema validation here (e.g., using jsonschema)
        if not isinstance(definition.get("tasks", {}), dict):
            raise ValueError("Workflow definition 'tasks' must be a dictionary.")
        # ... (More detailed validation for all parts of the definition)

    def _create_tasks(self):
        for task_id, task_def in self.tasks_definition.items():
            task_type = task_def.get("type")
            if task_type == "shell":
                self.tasks[task_id] = ShellTask(task_id, task_def, self)
            elif task_type == "rest":
                self.tasks[task_id] = RestApiTask(task_id, task_def, self)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
            self.task_results[task_id] = TaskResult(TaskStatus.PENDING)

    def execute(self, workflow_input: Dict[str, Any]):
        self.workflow_data["workflow"] = {"input": workflow_input}
        self._create_tasks()
        self.execution_status = TaskStatus.RUNNING
        logging.info(f"Workflow '{self.name} v{self.version}' started with input: {workflow_input}")

        executable_tasks = [task for task in self.tasks.values() if not task.depends_on]
        executed_tasks = set()

        while executable_tasks or len(executed_tasks) < len(self.tasks):
            next_executable_tasks = []
            for task in executable_tasks:
                if task.task_id not in executed_tasks and task.is_ready():
                    self.task_results[task.task_id] = TaskResult(TaskStatus.RUNNING)
                    result = task.execute()
                    self.task_results[task.task_id] = result
                    executed_tasks.add(task.task_id)
                    logging.info(f"Task '{task.task_id}' finished with status: {result.status}")

            executable_tasks = []
            for task in self.tasks.values():
                if task.task_id not in executed_tasks and all(dep in executed_tasks and self.task_results[dep].status == TaskStatus.COMPLETED for dep in task.depends_on):
                    executable_tasks.append(task)

            time.sleep(0.1) # Avoid busy-waiting

        all_completed = all(result.status == TaskStatus.COMPLETED for result in self.task_results.values())
        self.execution_status = TaskStatus.COMPLETED if all_completed else TaskStatus.FAILED
        logging.info(f"Workflow '{self.name}' execution finished with status: {self.execution_status}")
        return self.get_output()

    def get_task_output(self, task_id: str) -> Optional[Dict[str, Any]]:
        result = self.task_results.get(task_id)
        return result.output if result else None

    def evaluate_expression(self, expression: str) -> Any:
        # ... (More controlled and safer expression evaluation - potentially pre-processed)
        try:
            # Simplified example: Direct access only
            if expression.startswith("<span class="math-inline">\{workflow\.input\."\)\:
path \= expression\[16\:\-1\]\.split\('\.'\)
current \= self\.workflow\_data\.get\("workflow", \{\}\)\.get\("input", \{\}\)
for part in path\:
current \= current\.get\(part\)
if current is None\:
return None
return current
elif expression\.startswith\("</span>{tasks.") and expression.endswith(".output"):
                parts = expression[8:-7].split('.')
                task_id = parts[0]
                output_key = parts[1] if len(parts) > 1 else None
                task_output = self.get_task_output(task_id)
                return task_output.get(output_key) if task_output else None
            return expression # Fallback if no known pattern
        except Exception as e:
            logging.error(f"Error evaluating expression '{expression}': {e}")
            return None

    def get_output(self):
        if self.execution_status == TaskStatus.COMPLETED and self.output_schema:
            output_data = {}
            for key, value_template in self.output_schema.items():
                output_data[key] = self.evaluate_expression(value_template)
            return output_data
        else:
            return {"status": self.execution_status.value, "task_results": {tid: res.status.value for tid, res in self.task_results.items()}}


class MissionCriticalTask:
    def __init__(self, task_id: str, task_definition: Dict[str, Any], engine: WorkflowEngine):
        self.task_id = task_id
        self.type: str = task_definition.get("type")
        self.depends_on: List[str] = task_definition.get("depends_on", [])
        self.condition_expression: Optional[str] = task_definition.get("condition")
        self.config: Dict[str, Any] = task_definition.get("config", {})
        self.output_path: str = task_definition.get("output_path", task_id)
        self.engine: WorkflowEngine = engine

    def is_ready(self) -> bool:
        if not self.depends_on:
            return self._evaluate_condition()
        return all(self.engine.task_results.get(dep, TaskResult(TaskStatus.PENDING)).status == TaskStatus.COMPLETED for dep in self.depends_on) and self._evaluate_condition()

    def _evaluate_condition(self) -> bool:
        if self.condition_expression is None:
            return True
        result = self.engine.evaluate_expression(self.condition_expression)
        return bool(result) if result is not None else False

    def execute(self) -> TaskResult:
        raise NotImplementedError
    