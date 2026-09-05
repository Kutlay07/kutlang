import shlex
import fnmatch

from harness.policy.risk_classifier import RiskClassifier
from harness.policy.risk_level import RiskLevel
from harness.policy.tool_execution_request import ToolExecutionRequest

from harness.policy.risk_patterns import (
    FILESYSTEM_TOOLS,
    READ_ONLY_FILESYSTEM_TOOLS,
    WRITE_FILESYSTEM_TOOLS,
    DESTRUCTIVE_FILESYSTEM_TOOLS,
    EXECUTION_TOOLS,
    READ_ONLY_EXECUTION_TOOLS,
    PROCESS_CONTROL_EXECUTION_TOOLS,
    COMMAND_EXECUTION_TOOLS,
    PRIVILEGE_ESCALATION,
    PROCESS_COMMANDS,
    SYSTEM_DESTRUCTIVE,
    DEPENDENCY_MUTATION,
    READ_ONLY_GIT_COMMANDS,
    MEDIUM_GIT_COMMANDS,
    HIGH_GIT_COMMANDS,
    SENSITIVE_TARGET_PATTERNS,
)


class DefaultRiskClassifier(RiskClassifier):
    
    def classify(self, request: ToolExecutionRequest) -> RiskLevel:
        tool_name = request.tool_name
        risks = []
        if tool_name in FILESYSTEM_TOOLS:
            risks.append(self._classify_filesystem(request))
            
        if tool_name in EXECUTION_TOOLS:
            risks.append(self._classify_execution(request))
            
        sensitive_risk = self._classify_sensitive_target(request)
        
        if sensitive_risk is not None:
            risks.append(sensitive_risk)
            
        
        if risks:
            return max(risks)
        return RiskLevel.HIGH


    def _classify_filesystem(
        self,
        request: ToolExecutionRequest,
    ) -> RiskLevel | None:
    
        tool_name = request.tool_name
        
        if tool_name in READ_ONLY_FILESYSTEM_TOOLS:
            return RiskLevel.LOW
        
        if tool_name in WRITE_FILESYSTEM_TOOLS:
            return RiskLevel.MEDIUM
        
        if tool_name in DESTRUCTIVE_FILESYSTEM_TOOLS:
            return RiskLevel.HIGH
        
        return None


    def _classify_execution(
        self,
        request: ToolExecutionRequest,
    ) -> RiskLevel | None:
        tool_name = request.tool_name
        
        if tool_name in READ_ONLY_EXECUTION_TOOLS:
            return RiskLevel.LOW
        
        if tool_name in PROCESS_CONTROL_EXECUTION_TOOLS:
            return RiskLevel.HIGH
        
        if tool_name in COMMAND_EXECUTION_TOOLS:
            command = request.arguments.arguments["command"]
            
            if not isinstance(command, str):
                return RiskLevel.HIGH
            
            
            return self._classify_command(command)
        
        return None


    def _classify_sensitive_target(
        self,
        request: ToolExecutionRequest,
    ) -> RiskLevel | None:
        if request.arguments.arguments.get("path") is not None:
            path = request.arguments.arguments["path"]
            normalized = path.replace("\\", "/")
            basename = normalized.rsplit("/", 1)[-1]
            
            if any(fnmatch.fnmatch(basename, pattern)
                for pattern in SENSITIVE_TARGET_PATTERNS):
                    return RiskLevel.HIGH
        return None


    def _classify_command(
        self,
        command: str,
    ) -> RiskLevel:
        try:
            parts = shlex.split(command)
            if not parts:
                return RiskLevel.HIGH
            command_name = parts[0]
            if command_name in PROCESS_COMMANDS:
                if "-Verb" in parts:
                    index = parts.index("-Verb")
                    if index + 1 < len(parts):
                        if parts[index + 1] == "RunAs":
                            return RiskLevel.CRITICAL
                    return RiskLevel.HIGH
            
            if command_name in PRIVILEGE_ESCALATION:
                return RiskLevel.CRITICAL
            
            if command_name in SYSTEM_DESTRUCTIVE:
                return RiskLevel.CRITICAL
            
            program = parts[0]
            if len(parts) > 1:
                action = parts[1]
                if program + " " + action in DEPENDENCY_MUTATION:
                    return RiskLevel.MEDIUM
                if program + " " + action in READ_ONLY_GIT_COMMANDS:
                    return RiskLevel.LOW
                if program + " " + action in MEDIUM_GIT_COMMANDS:
                    return RiskLevel.MEDIUM
                if program + " " + action in HIGH_GIT_COMMANDS:
                    return RiskLevel.HIGH
            
            return RiskLevel.HIGH
        except ValueError:
            return RiskLevel.HIGH