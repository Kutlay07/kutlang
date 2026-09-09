from harness.policy.approval_handler import ApprovalHandler
from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult


class DefaultApprovalHandler(ApprovalHandler):
    
    async def handle(
        self,
        approval_request: ApprovalRequest,
    ) -> ApprovalResult:
        """Rejects approval requests by default when no approval surface is configured."""
        return ApprovalResult.REJECTED