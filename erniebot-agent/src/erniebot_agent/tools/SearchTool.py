import os
from typing import Dict, List, Optional, Type

import erniebot
from langchain.document_loaders import TextLoader
from langchain.text_splitter import SpacyTextSplitter
from langchain.vectorstores import FAISS
from pydantic import BaseModel, Field

from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.chat_models.erniebot import ERNIEBot
from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
from erniebot_agent.memory.whole_memory import WholeMemory
from erniebot_agent.messages import AIMessage, HumanMessage, Message
from erniebot_agent.tools.base import Tool, ToolParameterView


class SearchToolInputView(ToolParameterView):
    query: str = Field(description="用于检索故事情节的语句")


class SearchResponseDocument(ToolParameterView):
    document: str = Field(description="和query相关的故事情节片段")


class SearchToolOutputView(ToolParameterView):
    documents: List[SearchResponseDocument] = Field(description="检索结果，内容为故事剧情中和query相关的情节片段")


class SearchTool(Tool):
    description: str = "在故事情节中找到与用户输入最相关的片段"
    input_type: Type[ToolParameterView] = SearchToolInputView
    ouptut_type: Type[ToolParameterView] = SearchToolOutputView

    def __init__(self, db):
        self.db = db

    async def __call__(self, query: str) -> Dict[str, float]:
        docs = self.db.similarity_search(query)
        retrieval_results = []
        for doc in docs:
            retrieval_results.append(
                dict(
                    SearchResponseDocument(
                        document=doc.page_content,
                        filename=doc.metadata["source"],
                    )
                )
            )
        return {"documents": retrieval_results}

    @property
    def examples(self) -> List[Message]:
        return [
            HumanMessage("开始游戏"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户选择开始游戏，使用{self.tool_name}工具检索第一章相关的信息，检索的query：'第一回'。",
                    "arguments": '{"query": "第一回"}',
                },
            ),
        ]
