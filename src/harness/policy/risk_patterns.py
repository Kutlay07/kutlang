# filesystem
FILESYSTEM_TOOLS = frozenset({
    "append_file",
    "copy_file",
    "create_directory",
    "delete_directory",
    "delete_file",
    "directory_exists",
    "edit_file",
    "file_exists",
    "get_current_directory",
    "get_file_info",
    "list_directory",
    "move_file",
    "read_file",
    "write_file",
})

READ_ONLY_FILESYSTEM_TOOLS = frozenset({
    "get_current_directory",
    "file_exists",
    "directory_exists",
    "get_file_info",
    "list_directory",
    "read_file",
})

WRITE_FILESYSTEM_TOOLS = frozenset({
    "append_file",
    "copy_file",
    "create_directory",
    "edit_file",
    "move_file",
    "write_file",
})

DESTRUCTIVE_FILESYSTEM_TOOLS = frozenset({
    "delete_file",
    "delete_directory",
})


# execution
EXECUTION_TOOLS = frozenset({
    "get_process_output",
    "kill_process",
    "run_background_command",
    "run_command",
})

READ_ONLY_EXECUTION_TOOLS = frozenset({
    "get_process_output",
})

PROCESS_CONTROL_EXECUTION_TOOLS = frozenset({
    "kill_process",
})

COMMAND_EXECUTION_TOOLS = frozenset({
    "run_command",
    "run_background_command"
})

#
PRIVILEGE_ESCALATION = frozenset({
    "sudo",
    "runas",
})

PROCESS_COMMANDS = frozenset({
    "Start-Process",
})


SYSTEM_DESTRUCTIVE = frozenset({
    "mkfs",
    "fdisk",
    "dd",
    "wipefs",
    "format",
    "shutdown",
    "reboot",
})


DEPENDENCY_MUTATION = frozenset({
    "pip install",
    "uv add",
    "uv remove",
    "uv lock",
    "uv sync",
})


# git
READ_ONLY_GIT_COMMANDS = frozenset({
    "git status",
    "git diff",
    "git log",
    "git show",
    "git show",
    "git branch",
})

MEDIUM_GIT_COMMANDS = frozenset({
    "git add",
    "git commit",
    "git revert",
    "git checkout",
    "git switch",
    "git merge",
})

HIGH_GIT_COMMANDS = frozenset({
    "git push",
    "git reset",
    "git clean",
})


# sensitive
SENSITIVE_TARGET_PATTERNS = frozenset({
    ".env*",
})  