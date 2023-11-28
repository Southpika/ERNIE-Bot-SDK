from __future__ import annotations

from typing import Dict, List, Type

from erniebot_agent.messages import AIMessage, HumanMessage, Message
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.browser_main import Browser_Manager
from erniebot_agent.tools.schema import ToolParameterView
from pydantic import BaseModel, Field


class SearchToolInputView(ToolParameterView):
    query: str = Field(description="网络上搜索想要的答案的搜索语句")
    search_type: str = Field(description="网络搜索的类别，包括`search`, 'news'和`baike`，分别对应网络搜索,新闻搜索和百科搜索")


# class SearchType(BaseModel):
#     search:


class SearchToolOutputView(ToolParameterView):
    result: float = Field(description="在网络上搜索到的与query相关的片段")


class SearchTool(Tool):
    description: str = "通过网络搜索帮助用户在互联网上快速找到与query相关的片段用于增强回答"
    input_type: Type[ToolParameterView] = SearchToolInputView
    ouptut_type: Type[ToolParameterView] = SearchToolOutputView

    async def __call__(self, query: str, search_type: str) -> Dict[str, float]:
        browser = Browser_Manager(5)
        docs = browser.search(search_type, query)
        return {"documents": docs}

    @property
    def examples(self) -> List[Message]:
        return [
            HumanMessage("请告诉我孤注一掷这个电影怎么样？"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户想知道电影'孤注一掷'，我可以使用{self.tool_name}工具去网络上进行搜索，"
                    "其中用于检索的`query`字段的内容为：'孤注一掷电影评价如何'。",
                    "arguments": '{"query": "孤注一掷电影评价如何", "search_type": "search"}',
                },
            ),
            HumanMessage("帮我查一下三体是什么？"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户想知道'三体'的定义，我可以使用{self.tool_name}工具去网络的百科上进行搜索" "其中`query`字段的内容为：三体。",
                    "arguments": '{"query": "三体", "search_type": "baike"}',
                },
            ),
            HumanMessage("帮我在网络上搜索一下巴以冲突"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户想知道'巴以冲突'，我可以使用{self.tool_name}工具去网络上进行搜索"
                    "其中用于检索的`query`字段的内容为：'巴以冲突'。",
                    "arguments": '{"query": "巴以冲突", "search_type": "search"}',
                },
            ),
            HumanMessage("今天有什么新闻"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户想知道今天的新闻，我可以使用{self.tool_name}工具去网络上进行搜索今日新闻"
                    "其中用于检索的`query`字段的内容为：'今日新闻'。",
                    "arguments": '{"query": "今日新闻", "search_type": "news"}',
                },
            ),
        ]


import asyncio

if __name__ == "__main__":
    search_tool = SearchTool()
    references = asyncio.run(search_tool(search_type="search", query="孤注一掷怎么样"))
