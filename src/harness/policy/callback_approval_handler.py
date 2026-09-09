from collections.abc import Awaitable, Callable

from harness.policy.approval_handler import ApprovalHandler
from harness.policy.approval_request import ApprovalRequest
from harness.policy.approval_result import ApprovalResult


class CallbackApprovalHandler(ApprovalHandler):
    def __init__(
        self, 
        callback: Callable[[ApprovalRequest], Awaitable[ApprovalResult]]
        ):
    
        self.callback = callback


    async def handle(
        self,
        approval_request: ApprovalRequest,
        ) -> ApprovalResult:
        return await self.callback(approval_request)