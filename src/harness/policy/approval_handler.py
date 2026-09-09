from typing import Protocol

from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult


class ApprovalHandler(Protocol):
    
    async def handle(
        self,
        approval_request: ApprovalRequest,
        ) -> ApprovalResult:
        ...