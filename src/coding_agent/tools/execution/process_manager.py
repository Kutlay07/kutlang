import subprocess


class ProcessManager:
    def __init__(self):
        self._processes: dict[int, subprocess.Popen] = {}

    def add(self, process: subprocess.Popen) -> None:
        self._processes[process.pid] = process

    def get(self, process_id: int) -> subprocess.Popen:
        return self._processes[process_id]

    def remove(self, process_id: int) -> None:
        del self._processes[process_id]