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

from typing import AsyncGenerator, List, Optional, Union

import gradio as gr
from erniebot_agent.agents.base import Agent, ToolManager
from erniebot_agent.agents.callback.callback_manager import CallbackManager
from erniebot_agent.agents.callback.handlers.base import CallbackHandler
from erniebot_agent.agents.schema import AgentAction, AgentFile, AgentResponse
from erniebot_agent.chat_models.base import ChatModel
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.memory.base import Memory
from erniebot_agent.messages import (
    FunctionMessage,
    HumanMessage,
    Message,
    SystemMessage,
)
from erniebot_agent.tools.base import Tool

""" 
假设有一个方法tool choice为强制使用某工具（auto/None/tool✅），用法为
response = erniebot.ChatCompletion.create(
    model='ernie-bot-4',
    messages=messages,
    functions=functions,
    tool_choice={"type": "function", "function": {"name": "toolA"},
)
"""
class ManualAgent(Agent):
    def __init__(
            self, 
            llm: ChatModel,
            memory: Memory, 
            tools: Union[ToolManager, List[Tool]],
            tool_sequence: List[Tool],
            system_message: str = None,
            file_manager: FileManager = FileManager(),
        ):

        super().__init__(
            llm=llm, 
            memory=memory, 
            tools=tools, 
            system_message=SystemMessage(system_message),
            file_manager=file_manager
        )
        self.file_manager = file_manager
        self.tool_sequence = tool_sequence


    async def _async_run(self, prompt: str) -> AgentResponse:
        chat_history: List[Message] = []
        actions_taken: List[AgentAction] = []
        files_involved: List[AgentFile] = []
        ask = HumanMessage(content=prompt)

        next_step_input: Message = ask
        for tool in self.tool_sequence:            
            curr_step_output = await self._async_step(
                next_step_input, chat_history, actions_taken, files_involved, tool
            )                

            next_step_input = curr_step_output

        self.memory.add_message(chat_history[0])
        self.memory.add_message(chat_history[-1])
        response = self._create_finished_response(chat_history, actions_taken, files_involved)
        return response


    async def _async_step(
        self,
        step_input,
        chat_history: List[Message],
        actions: List[AgentAction],
        files: List[AgentFile],
        tool
    ) -> Optional[Message]:
        
        maybe_action = await self._async_plan(step_input, chat_history, tool)
        if isinstance(maybe_action, AgentAction):
            action: AgentAction = maybe_action
            tool_resp = await self._async_run_tool(tool_name=action.tool_name, tool_args=action.tool_args)
            actions.append(action)
            files.extend(tool_resp.files)
            return FunctionMessage(name=action.tool_name, content=tool_resp.json)


    async def _async_plan(
        self, input_message: Message, chat_history: List[Message], tool
    ) -> Optional[AgentAction]:
        chat_history.append(input_message)
        messages = self.memory.get_messages() + chat_history
        if tool:
            llm_resp = await self._async_run_llm(
                messages=messages,
                functions=self._tool_manager.get_tool_schemas(),
                system=self.system_message.content if self.system_message is not None else None,
                tool_choice=tool,
            )
            output_message = llm_resp.message
            chat_history.append(output_message)
            # 如果output_message.function_call没有触发？
            return AgentAction(
                tool_name=output_message.function_call["name"],  # type: ignore
                tool_args=output_message.function_call["arguments"],
            )
        else:
            llm_resp = await self._async_run_llm(
                messages=messages,
                system=self.system_message.content if self.system_message is not None else None,
            )
            output_message = llm_resp.message
            chat_history.append(output_message)
            return None
        
    def _create_finished_response(
        self,
        chat_history: List[Message],
        actions: List[AgentAction],
        files: List[AgentFile],
    ) -> AgentResponse:
        last_message = chat_history[-1]
        return AgentResponse(
            text=last_message.content,
            chat_history=chat_history,
            actions=actions,
            files=files,
            status="FINISHED",
        )
