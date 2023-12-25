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

import asyncio
import io
import os
import uuid
from typing import Dict, List, Optional, Type

from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.messages import AIMessage, HumanMessage, Message
from erniebot_agent.tools.base import RemoteToolkit, Tool
from erniebot_agent.tools.schema import ToolParameterView
from erniebot_agent.utils.common import download_file, get_cache_dir
from PIL import Image
from pydantic import Field

API_URL = "https://aistudio.baidu.com/bd-gpu-04/user/732872/7155718/api_serving/8080"

HEADERS = {
    # 请前往 https://aistudio.baidimage.pngu.com/index/accessToken 查看 访问令牌 并替换
    "Authorization": "token 7d109d14c26a3e0e5a01f841927c30331ad07e62",
    "Content-Type": "application/json",
}


def bytestr_to_png(bytestr, output_path):
    # 将字节字符串转换为BytesIO对象
    image_bytes = io.BytesIO(bytestr)
    # 打开BytesIO对象作为图像
    image = Image.open(image_bytes)
    # 将图像保存为PNG格式
    image.save(output_path, format="PNG")
    print("图片已保存到：" + output_path)
    image.show()


class ImageGenerationInputView(ToolParameterView):
    prompt: str = Field(description="描述图像内容、风格的文本。例如：生成一张月亮的照片，月亮很圆。")
    width: Optional[int] = Field(description="生成图片的宽度")
    height: Optional[int] = Field(description="生成图片的高度")
    image_num: Optional[int] = Field(description="生成图片的数量")


class ImageGenerationOutputView(ToolParameterView):
    img_bytes: bytes = Field(description="图片的二进制文件")


class ImageGenerationTool(Tool):
    description: str = "AI作图、生成图片、画图的工具"
    input_type: Type[ToolParameterView] = ImageGenerationInputView
    ouptut_type: Type[ToolParameterView] = ImageGenerationOutputView

    def __init__(self) -> None:
        self.file_manager = FileManager()
        return
        remote_file_client = BOSFileClient(
            ak="8343f27745d74e6f97c99de824cd8866",
            sk="7270c84056034bd5a112b43f952aaf34",
            bucket_name="gdfdudu",
            prefix="erniebot-agent/",
        )
        # self.file_manager = FileManager(remote_file_client=remote_file_client, auto_register=True)
        # return
        self.toolkit = RemoteToolkit.from_url(
            API_URL, access_token="7d109d14c26a3e0e5a01f841927c30331ad07e62"
        )
        self.file_manager = FileManager(remote_file_client=remote_file_client, auto_register=True)

    async def __call__(
        self,
        prompt: str,
    ) -> bytes:
        tool_name = "textToImage"

        # text_to_image_tool = self.toolkit.get_tool(tool_name)
        # response = await text_to_image_tool(text=prompt)
        # result = {'file_id':response['return_file']}
        # return result
        # FOR MOCK
        image_path = r"/Users/tanzhehao/Documents/ERINE/text_to_image.png"
        file = await self.file_manager.create_file_from_path(file_path=image_path, file_type="local")
        file
        # image = Image.open(image_path)

        # with io.BytesIO() as byte_buffer:
        #     image.save(byte_buffer,'png')
        #     byte_str = byte_buffer.getvalue()

        # image.show()

        result = {"file_id": file.id}
        return result

    @property
    def examples(self) -> List[Message]:
        return [
            HumanMessage("画一张小狗的图片，图像高度512，图像宽度512"),
            AIMessage(
                "",
                function_call={
                    "name": "ImageGenerationTool",
                    "thoughts": "用户需要我生成一张小狗的图片，图像高度为512，宽度为512。我可以使用ImageGenerationTool工具来满足用户的需求。",
                    "arguments": '{"prompt":"画一张小狗的图片，图像高度512，图像宽度512",'
                    '"width":512,"height":512,"image_num":1}',
                },
            ),
            HumanMessage("生成两张天空的图片"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": "用户想要生成两张天空的图片，我需要调用ImageGenerationTool工具的call接口，"
                    "并设置prompt为'生成两张天空的图片'，width和height可以默认为512，image_num默认为2。",
                    "arguments": '{"prompt":"生成两张天空的图片","width":512,"height":512,"image_num":2}',
                },
            ),
            HumanMessage("使用AI作图工具，生成1张小猫的图片，高度和高度是1024"),
            AIMessage(
                "",
                function_call={
                    "name": self.tool_name,
                    "thoughts": "用户需要生成一张小猫的图片，高度和宽度都是1024。我可以使用ImageGenerationTool工具来满足用户的需求。",
                    "arguments": '{"prompt":"生成一张小猫的照片。","width":1024,"height":1024,"image_num":1}',
                },
            ),
        ]


if __name__ == "__main__":
    img_tool = ImageGenerationTool()
    # asyncio.run(img_tool("a cute dod"))
    print(img_tool.function_call_schema())