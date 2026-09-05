from harness.policy.default_risk_classifier import DefaultRiskClassifier
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_arguments import ToolArguments
from harness.policy.tool_execution_request import ToolExecutionRequest


def test_get_process_output_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="get_process_output",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_read_file_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_list_directory_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="list_directory",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_get_current_directory_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="get_current_directory",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_file_exists_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="file_exists",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_directory_exists_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="directory_exists",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_get_file_info_is_low():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="get_file_info",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.LOW


def test_append_file_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="append_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_copy_file_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="copy_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_create_directory_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="create_directory",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_edit_file_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="edit_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_move_file_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="move_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_write_file_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="write_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_delete_file_is_high():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="delete_file",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.HIGH


def test_delete_directory_is_high():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="delete_directory",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.HIGH


def test_kill_process_is_high():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="kill_process",
        arguments=ToolArguments({}),
    )
    
    assert classifier.classify(request) == RiskLevel.HIGH


def test_pip_install_is_medium():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "pip install requests",
            }),
    )
    
    assert classifier.classify(request) == RiskLevel.MEDIUM


def test_read_file_env_is_high():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({
            "path": ".env",
            }),
    )
    
    assert classifier.classify(request) == RiskLevel.HIGH


def test_read_file_env_local_is_high():
    classifier = DefaultRiskClassifier()
    
    request = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({
            "path": "/path/to/.env.local",
            }),
    )
    
    assert classifier.classify(request) == RiskLevel.HIGH


def test_risk_level_high_is_bigger_than_risk_level_medium():
    assert RiskLevel.HIGH > RiskLevel.MEDIUM


def test_same_tool_gives_different_risk_due_to_argument():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({
            "path": "/path/to/.env.local",
            }),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="read_file",
        arguments=ToolArguments({
            "path": "/path/to/main.py",
            }),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    
    assert request1_risk != request2_risk


def test_unknown_failed_closed_commands_and_tools_return_high_risk():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="unknown_tool",
        arguments=ToolArguments({}),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "unknown_command"
            }),
    )
    
    request3 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": " "}),
    )
    
    request4 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "abidubidi"
            }),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    request3_risk = classifier.classify(request3)
    request4_risk = classifier.classify(request4)
    
    assert request1_risk == RiskLevel.HIGH
    assert request2_risk == RiskLevel.HIGH
    assert request3_risk == RiskLevel.HIGH
    assert request4_risk == RiskLevel.HIGH


def test_risk_aggregation():
    assert max(RiskLevel.MEDIUM, RiskLevel.HIGH) == RiskLevel.HIGH


def test_git_low():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git status",
            }),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git branch"
            }),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    
    assert request1_risk == RiskLevel.LOW
    assert request2_risk == RiskLevel.LOW


def test_git_medium():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git checkout"}),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git switch"
            }),
    )
    
    request3 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git merge"}),
    )
    
    request4 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git add",
            }),
    )
    
    request5 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git commit",
            }),
    )
    
    request6 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git revert",
            }),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    request3_risk = classifier.classify(request3)
    request4_risk = classifier.classify(request4)
    request5_risk = classifier.classify(request5)
    request6_risk = classifier.classify(request6)
    
    assert request1_risk == RiskLevel.MEDIUM
    assert request2_risk == RiskLevel.MEDIUM
    assert request3_risk == RiskLevel.MEDIUM
    assert request4_risk == RiskLevel.MEDIUM
    assert request5_risk == RiskLevel.MEDIUM
    assert request6_risk == RiskLevel.MEDIUM


def test_git_high():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git push",
            }),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git reset",
            }),
    )
    
    request3 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "git clean",
            }),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    request3_risk = classifier.classify(request3)
    
    assert request1_risk == RiskLevel.HIGH
    assert request2_risk == RiskLevel.HIGH
    assert request3_risk == RiskLevel.HIGH


def test_uv_mediums():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "uv add requests"}),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "uv remove requests"
            }),
    )
    
    request3 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "uv lock"}),
    )
    
    request4 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "uv sync"}),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    request3_risk = classifier.classify(request3)
    request4_risk = classifier.classify(request4)
    
    assert request1_risk == RiskLevel.MEDIUM
    assert request2_risk == RiskLevel.MEDIUM
    assert request3_risk == RiskLevel.MEDIUM
    assert request4_risk == RiskLevel.MEDIUM


def test_process_commands_are_not_case_sensitive():
    classifier = DefaultRiskClassifier()
    
    request1 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "start-process -verb runas"}),
    )
    
    request2 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "Start-Process -verb runas"}),
    )
    
    request3 = ToolExecutionRequest(
        tool_name="run_command",
        arguments=ToolArguments({
            "command": "START-PROCESS -VERB RUNAS"}),
    )
    
    request1_risk = classifier.classify(request1)
    request2_risk = classifier.classify(request2)
    request3_risk = classifier.classify(request3)
    
    assert request1_risk == RiskLevel.CRITICAL
    assert request2_risk == RiskLevel.CRITICAL
    assert request3_risk == RiskLevel.CRITICAL