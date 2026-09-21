from harness.tools.base_tool import BaseTool
from harness.tools.search.provider import SearchToolProvider


def test_search_tool_provider_returns_tools(
    workspace_boundary,
    search_visibility,
    output_budget
    ):
    provider = SearchToolProvider(
        workspace_boundary,
        search_visibility,
        output_budget,
        )

    tools = provider.get_tools()

    assert isinstance(tools, list)
    assert all(isinstance(tool, BaseTool) for tool in tools)