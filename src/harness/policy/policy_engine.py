from typing import Protocol

from harness.policy.policy_context import PolicyContext
from harness.policy.policy_evaluation import PolicyEvaluation


class PolicyEngine(Protocol):
    
    def evaluate(
        self,
        policy_context: PolicyContext,
        ) -> PolicyEvaluation:
        ...