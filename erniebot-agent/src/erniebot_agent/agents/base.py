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

from typing import Any, List, Optional, Protocol, TypeVar, runtime_checkable

from erniebot_agent.agents.schema import AgentResponse, LLMResponse, ToolResponse
from erniebot_agent.chat_models.base import ChatModel
from erniebot_agent.file.base import File
from erniebot_agent.file.file_manager import FileManager
from erniebot_agent.memory import Memory
from erniebot_agent.memory.messages import Message
from erniebot_agent.tools.base import BaseTool

LLMT = TypeVar("LLMT", bound=ChatModel)


class BaseAgent(Protocol[LLMT]):
    llm: LLMT
    memory: Memory

    async def run(self, prompt: str, files: Optional[List[File]] = None) -> AgentResponse:
        ...

    async def run_tool(self, tool_name: str, tool_args: str) -> ToolResponse:
        ...

    async def run_llm(self, messages: List[Message], **opts: Any) -> LLMResponse:
        ...

    def load_tool(self, tool: BaseTool) -> None:
        ...

    def unload_tool(self, tool: BaseTool) -> None:
        ...

    def get_tools(self) -> List[BaseTool]:
        ...

    def reset_memory(self) -> None:
        ...

    async def get_file_manager(self) -> FileManager:
        ...


<<<<<<< HEAD
    @final
    async def _async_run_llm(self, messages: List[Message], **opts: Any) -> LLMResponse:
        await self._callback_manager.on_llm_start(agent=self, llm=self.llm, messages=messages)
        try:
            llm_resp = await self._async_run_llm_without_hooks(messages, **opts)
        except (Exception, KeyboardInterrupt) as e:
            await self._callback_manager.on_llm_error(agent=self, llm=self.llm, error=e)
            raise
        await self._callback_manager.on_llm_end(agent=self, llm=self.llm, response=llm_resp)
        return llm_resp

    async def _async_run_tool_without_hooks(self, tool: BaseTool, tool_args: str) -> ToolResponse:
        parsed_tool_args = self._parse_tool_args(tool_args)
        # XXX: Sniffing is less efficient and probably unnecessary.
        # Can we make a protocol to statically recognize file inputs and outputs
        # or can we have the tools introspect about this?
        input_files = await self._sniff_and_extract_files_from_args(parsed_tool_args, tool, "input")
        tool_ret = await tool(**parsed_tool_args)
        output_files = await self._sniff_and_extract_files_from_args(tool_ret, tool, "output")
        if output_files:
            tool_ret["prompt"] = "请你把FileID，如file-开头的字符串当作是文件内容，不要出现file-的字符串。"
        tool_ret_json = json.dumps(tool_ret, ensure_ascii=False)
        return ToolResponse(json=tool_ret_json, files=input_files + output_files)

    async def _async_run_llm_without_hooks(
        self, messages: List[Message], functions=None, **opts: Any
    ) -> LLMResponse:
        llm_ret = await self.llm.async_chat(messages, functions=functions, stream=False, **opts)
        return LLMResponse(message=llm_ret)

    def _parse_tool_args(self, tool_args: str) -> Dict[str, Any]:
        try:
            args_dict = json.loads(tool_args)
        except json.JSONDecodeError:
            raise ValueError(f"`tool_args` cannot be parsed as JSON. `tool_args`: {tool_args}")

        if not isinstance(args_dict, dict):
            raise ValueError(f"`tool_args` cannot be interpreted as a dict. `tool_args`: {tool_args}")
        return args_dict

    async def _sniff_and_extract_files_from_args(
        self, args: Dict[str, Any], tool: BaseTool, file_type: Literal["input", "output"]
    ) -> List[AgentFile]:
        agent_files: List[AgentFile] = []
        for val in args.values():
            if isinstance(val, str):
                if protocol.is_file_id(val):
                    file_manager = await self._get_file_manager()
                    try:
                        file = file_manager.look_up_file_by_id(val)
                    except FileError as e:
                        raise FileError(
                            f"Unregistered file with ID {repr(val)} is used by {repr(tool)}."
                            f" File type: {file_type}"
                        ) from e
                    agent_files.append(AgentFile(file=file, type=file_type, used_by=tool.tool_name))
            elif isinstance(val, dict):
                agent_files.extend(await self._sniff_and_extract_files_from_args(val, tool, file_type))
            elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                for item in val:
                    agent_files.extend(await self._sniff_and_extract_files_from_args(item, tool, file_type))
        return agent_files

    async def _get_file_manager(self) -> FileManager:
        if self._file_manager is None:
            file_manager = await GlobalFileManagerHandler().get()
        else:
            file_manager = self._file_manager
        return file_manager
=======
@runtime_checkable
class AgentLike(Protocol):
    async def run(self, prompt: str, files: Optional[List[File]] = None) -> AgentResponse:
        ...
>>>>>>> upstream/develop
