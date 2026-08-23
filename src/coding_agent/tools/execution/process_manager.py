from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class ManagedProcess:
    process: subprocess.Popen
    stdout_path: Path
    stderr_path: Path


class ProcessManager:
    def __init__(self):
        self._processes: dict[int, ManagedProcess] = {}

    def add(self, managed_process: ManagedProcess) -> None:
        self._processes[managed_process.process.pid] = managed_process

    def get(self, process_id: int) -> ManagedProcess:
        return self._processes[process_id]

    def remove(self, process_id: int) -> ManagedProcess:
        return self._processes.pop(process_id)
