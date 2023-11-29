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

import io
import os
import uuid
from typing import Dict, List, Optional, Type

from erniebot_agent.messages import AIMessage, HumanMessage, Message
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.schema import ToolParameterView
from erniebot_agent.utils.common import download_file, get_cache_dir
from erniebot_agent.tools.base import RemoteToolkit
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.file_io.remote_file_clients.bos_file_client import BOSFileClient
from pydantic import Field
from PIL import Image

import erniebot



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
    # image.show()

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

        remote_file_client = BOSFileClient(
            ak="8343f27745d74e6f97c99de824cd8866",
            sk="7270c84056034bd5a112b43f952aaf34",
            bucket_name="gdfdudu",
            prefix="erniebot-agent/",
        )
        self.file_manager = FileManager(remote_file_client=remote_file_client, auto_register=True)
        return
        self.toolkit = RemoteToolkit.from_url(
            API_URL, access_token="7d109d14c26a3e0e5a01f841927c30331ad07e62"
        )

        

    async def __call__(
        self,
        prompt: str,
        width: Optional[int] = 512,
        height: Optional[int] = 512,
        image_num: Optional[int] = 1,
    ) -> bytes:
        
        # tool_name = "textToImage"
        # text_to_image_tool = self.toolkit.get_tool(tool_name)
        # res = await text_to_image_tool(text=prompt)  # json error 补充
        # remote_file = await self.file_manager.retrieve_remote_file(res["file_id"])
        # byte_str = await remote_file.read_content()  # TODO: transfer to image
        # await remote_file.delete()

        # FOR MOCK
        image_path = r"/Users/tanzhehao/Documents/ERINE/text_to_image.png" 
        image = Image.open(image_path)
        
        with io.BytesIO() as byte_buffer:
            image.save(byte_buffer,'png')  
            byte_str = byte_buffer.getvalue()

        # image.show()

        byte_str = '/private/var/folders/gw/lbw__qt16dl3sdh_5cgv_jl00000gn/T/gradio/temp_8.png'
        return byte_str

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

