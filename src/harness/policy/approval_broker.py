from typing import Protocol

from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult


class ApprovalBroker(Protocol):
    
    async def request_approval(
        self,
        approval_request: ApprovalRequest,
    ) -> ApprovalResult:
        ...