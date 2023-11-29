# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union

from erniebot_agent.agents.callback.handlers.base import CallbackHandler
from erniebot_agent.agents.schema import AgentResponse
from erniebot_agent.chat_models.base import ChatModel
from erniebot_agent.messages import Message
from erniebot_agent.tools.base import Tool
from erniebot_agent.utils.json import to_pretty_json
from erniebot_agent.utils.text_color import color_text
from erniebot_agent.utils.logging import logger as default_logger

if TYPE_CHECKING:
    from erniebot_agent.agents.base import Agent


class LoggingHandler(CallbackHandler):
    logger: logging.Logger

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__()
        if logger is None:
            self.logger = default_logger
        else:
            self.logger = logger

    async def on_run_start(self, agent: Agent, prompt: str) -> None:
        self.agent_info(
            "%s is about to start running with input: %s\n",
            agent.__class__.__name__,
            prompt,
            subject="Run",
            state="Start",
        )

    async def on_llm_start(self, agent: Agent, llm: ChatModel, messages: List[Message]) -> None:
        # TODO: Prettier messages
        self.agent_info(
            "%s is about to start running with input:\n%s\n",
            llm.__class__.__name__,
            messages,
            subject="LLM",
            state="Start",
        )

    async def on_llm_end(self, agent: Agent, llm: ChatModel, response: Message) -> None:
        self.agent_info(
            "%s finished running with output: %s\n",
            llm.__class__.__name__,
            response,
            subject="LLM",
            state="End",
        )

    async def on_llm_error(
        self, agent: Agent, llm: ChatModel, error: Union[Exception, KeyboardInterrupt]
    ) -> None:
        pass

    async def on_tool_start(self, agent: Agent, tool: Tool, input_args: str) -> None:
        self.agent_info(
            "%s is about to start running with input:\n%s\n",
            tool.__class__.__name__,
            to_pretty_json(input_args, from_json=True),
            subject="Tool",
            state="Start",
        )

    async def on_tool_end(self, agent: Agent, tool: Tool, response: str) -> None:
        self.agent_info(
            "%s finished running with output:\n%s\n",
            tool.__class__.__name__,
            to_pretty_json(response, from_json=True),
            subject="Tool",
            state="End",
        )

    async def on_tool_error(
        self, agent: Agent, tool: Tool, error: Union[Exception, KeyboardInterrupt]
    ) -> None:
        pass

    async def on_run_end(self, agent: Agent, response: AgentResponse) -> None:
        self.agent_info("%s finished running.\n", agent.__class__.__name__, subject="Run", state="End")

    def agent_info(self, msg: str, *args, subject, state, **kwargs) -> None:
        msg = f"[{subject}][{state}] {msg}"
        self.logger.info(msg, *args, **kwargs)

    def agent_error(self, error: Union[Exception, KeyboardInterrupt], *args, subject, **kwargs) -> None:
        error_msg = f"[{subject}][ERROR] {error}"
        self.logger.error(error_msg, *args, **kwargs)
