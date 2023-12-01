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

import os
import asyncio
import queue
import threading
import time
from typing import AsyncGenerator, List, Optional, Union

import gradio as gr
from erniebot_agent.agents.base import Agent
from erniebot_agent.agents.schema import ToolResponse
from erniebot_agent.chat_models.erniebot import ERNIEBot
from erniebot_agent.memory.base import Memory
from erniebot_agent.memory.sliding_window_memory import SlidingWindowMemory
from erniebot_agent.messages import AIMessage, HumanMessage, SystemMessage
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.ImageGenerateTool import ImageGenerationTool
from erniebot_agent.tools.tool_manager import ToolManager
from erniebot_agent.utils.logging import logger
from erniebot_agent.file_io.file_manager import FileManager

class ManualAgent(Agent):
    def __init__(
            self, 
            model: str,
            memory: Memory, 
            tools: Union[ToolManager, List[Tool]],
            system_message: str,
            file_manager: Optional[FileManager] = None,
            access_token: str = None
        ):
        if not access_token: access_token = os.getenv("EB_ACCESS_TOKEN")
        super().__init__(
            llm=ERNIEBot(model, access_token=access_token), 
            memory=memory, 
            tools=tools, 
            system_message=SystemMessage(system_message),
            file_manager=file_manager
        )

        
        self.prompt_template = "你的指令是为我提供一个基于以下。并遵循以下特定格式。" 
                                 

        tool_prompt = "你可以使用以下Tools来帮助你完成这个任务。"               
        for tool in self._tool_manager.get_tools():
            tool_prompt += f"[Tool Name]: {tool.tool_name} \
                            [Tool Description]: {tool.description} \n"


    async def _async_run(self, prompt: str) -> AsyncGenerator:
        """Defualt open stream for threading tool call

        Args:
        prompt: str, the prompt for the tool
        """

        actual_query = prompt 
        messages = self.memory.get_messages() + [HumanMessage(actual_query)]
        response = await self.llm.async_chat(messages, stream=True, system=self.system_message.content)

        apply = False
        res = ""
        function_part = None
        thread = None

        async for temp_res in response:
            for s in temp_res.content:
                # 用缓冲区来达成一个字一个字输出的流式
                res += s
                time.sleep(0.005)
                yield s, function_part, thread 

                if res.count("```") == 2 and not apply:  # TODO 判断逻辑待更改
                    function_part = res[res.find("```") : res.rfind("```") + 3]
                    tool = eval(function_part[function_part.find("{") : function_part.rfind("}") + 1])
                    # TODO：线程修改为异步函数
                    # loop = asyncio.get_running_loop()
                    # task = loop.create_task
                    thread = threading.Thread(
                        target=self.handle_tool, args=(tool["tool_name"], tool["tool_args"])
                    )
                    thread.start()
                    apply = True
        # await task

        self.memory.add_message(HumanMessage(prompt))
        self.memory.add_message(AIMessage(content=res, function_call=None))

    def launch_gradio_demo(self) -> None:
        with gr.Blocks() as demo:
            context_chatbot = gr.Chatbot(label=self.script, height=750)
            input_text = gr.Textbox(label="消息内容", placeholder="请输入...")

            with gr.Row():
                start_buttton = gr.Button("开始游戏")
                remake_buttton = gr.Button("重新开始")

            remake_buttton.click(self.reset_memory)
            start_buttton.click(
                self._handle_gradio_chat,
                [start_buttton, context_chatbot],
                [input_text, context_chatbot],
                queue=False,
            ).then(self._handle_gradio_stream, context_chatbot, context_chatbot)
            input_text.submit(
                self._handle_gradio_chat,
                [input_text, context_chatbot],
                [input_text, context_chatbot],
                queue=False,
            ).then(self._handle_gradio_stream, context_chatbot, context_chatbot)
        demo.launch()

    def _handle_gradio_chat(self, user_message, history) -> tuple[str, List[tuple[str, str]]]:
        # 用于处理gradio的chatbot返回
        return "", history + [[user_message, None]]

    async def _handle_gradio_stream(self, history) -> AsyncGenerator:
        # 用于处理gradio的流式
        global FILE_QUEUE
        bot_response = self._async_run(history[-1][0])
        history[-1][1] = ""
        async for temp_response in bot_response:
            function_part = temp_response[1]
            thread = temp_response[2]
            history[-1][1] += temp_response[0]
            yield history
        else:
            if thread:
                thread.join()
                tool_response: ToolResponse = FILE_QUEUE.get()
                img_path = eval(tool_response.json)["return_path"]
                img_path = img_path.strip('"')  # 去除json.dump的引号
                logger.debug("end" + img_path)

            if function_part:
                history[-1][1] = history[-1][1].replace(
                    function_part,
                    f"<img src='file={img_path}' alt='Example Image' width='400' height='300'>",
                )
            yield history

