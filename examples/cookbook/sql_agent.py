import argparse
import asyncio
import os
import time
from typing import Any, AsyncGenerator, List, Optional, Tuple, Union

import gradio as gr
from erniebot_agent.agents.base import Agent
from erniebot_agent.agents.schema import AgentFile
from erniebot_agent.chat_models.erniebot import ERNIEBot
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.memory.sliding_window_memory import SlidingWindowMemory
from erniebot_agent.messages import AIMessage, HumanMessage, SystemMessage
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.ImageGenerateTool import (
    ImageGenerationTool,  # 目前为remotetool，如做直接展示可以替换为yinian
)
from erniebot_agent.tools.tool_manager import ToolManager
from erniebot_agent.chat_models.erniebot import ERNIEBot


# unset EB_BASE_URL
llm = ERNIEBot(model="ernie-bot-4", api_type='aistudio', access_token=os.getenv('EB_ACCESS_TOKEN'))

class SQLAgent(Agent):
    def __init__(
        self,
        model: str,
        script: str,
        tools: Union[ToolManager, List[Tool]],
        system_message: Optional[SystemMessage] = None,
        access_token: Union[str, None] = None,
        max_round: int = 3,
    ) -> None:
        self.script = script
        memory = SlidingWindowMemory(max_round)

        super().__init__(
            llm=ERNIEBot(model, api_type="aistudio", access_token=access_token),
            memory=memory,
            tools=tools,
            system_message=system_message,
        )
        self.file_manager: FileManager = FileManager()
    
    