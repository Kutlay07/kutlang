from harness.policy.approval_broker import ApprovalBroker
from harness.policy.approval_handler import ApprovalHandler
from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult


class DefaultApprovalBroker(ApprovalBroker):
    def __init__(
        self,
        handler: ApprovalHandler,
        ):
        self.handler = handler
        
    async def request_approval(
        self,
        approval_request: ApprovalRequest,
    ) -> ApprovalResult:
        return await self.handler.handle(approval_request)