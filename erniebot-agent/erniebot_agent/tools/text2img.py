from __future__ import annotations

import asyncio
import os
from typing import Dict, List, Type

import webuiapi
from erniebot_agent.messages import AIMessage, HumanMessage, Message
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.browser_main import Browser_Manager
from erniebot_agent.tools.schema import ToolParameterView
from pydantic import BaseModel, Field


def get_img(prompt: str) -> None:
    api = webuiapi.WebUIApi(host="10.21.226.177", port=8544)
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp.png")

    result1 = api.txt2img(
        prompt=prompt,
        negative_prompt="ugly, out of frame",
        seed=1003,
        styles=["anime"],
        cfg_scale=7,
    )

    result1.image.save(output_dir)
    return output_dir


class ImageGenerateToolInputView(ToolParameterView):
    query: str = Field(description="用于生成图片的提示语（英语）")
    style: str = Field(description="生成图片的风格")


class ImageGenerateToolOutputView(ToolParameterView):
    output_dir: float = Field(description="生成图片的路径")


class ImageGenerateTool(Tool):
    description: str = "ImageGenerateTool用于根据用户的文字提示，生成图片。"
    input_type: Type[ToolParameterView] = ImageGenerateToolInputView
    ouptut_type: Type[ToolParameterView] = ImageGenerateToolOutputView

    async def __call__(self, query: str, style: str) -> str:
        output_dir = get_img(query)
        return {"output_dir": output_dir}

    @property
    def examples(self) -> List[Message]:
        return [
            HumanMessage("请帮我画一只小狗"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": f"用户想画一只小狗，我可以使用{self.tool_name}工具来画图，其中`query`字段需要为英语，内容为：'a cute dog'。",
                    "arguments": '{"query": "a cute dog", "style": "anime"}',
                },
            ),
        ]


async def main():
    from erniebot_agent.agents.functional_agent import FunctionalAgent
    from erniebot_agent.chat_models.erniebot import ERNIEBot
    from erniebot_agent.memory.whole_memory import WholeMemory

    import erniebot

    erniebot.api_type = "aistudio"
    erniebot.access_token = os.getenv("EB_ACCESS_TOKEN")
    tool = ImageGenerateTool()
    llm = ERNIEBot(model="ernie-bot")
    memory = WholeMemory()
    agent = FunctionalAgent(llm=llm, tools=[tool], memory=memory)
    query = "画一张寺庙的图，里面有很多长老"
    response = await agent.async_run(query)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
