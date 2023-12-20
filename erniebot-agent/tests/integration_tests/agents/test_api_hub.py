from __future__ import annotations

import os
import unittest

import pytest
from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.memory import WholeMemory
from erniebot_agent.tools import RemoteToolkit
from erniebot_agent.tools.tool_manager import ToolManager

os.environ["EB_MAX_RETRIES"] = "100"


class TestOCRRemotePlugin(unittest.IsolatedAsyncioTestCase):
    def get_agent(self, toolkit: RemoteToolkit):
        # llm = ERNIEBot(model="ernie-bot-4")
        llm = ERNIEBot(
            model="ernie-bot", api_type="aistudio", access_token='1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb'
        )

        agent = FunctionalAgent(
            llm=llm,
            tools=ToolManager(tools=toolkit.get_tools()),
            memory=WholeMemory(),
        )
        return agent

    # @pytest.mark.asyncio
    # async def test_plugin_text_moderation(self):
    #     url = "https://tool-text-moderation.aistudio-hub.baidu.com"
    #     toolkit = RemoteToolkit.from_url(url, version="v1.1", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

    #     agent = self.get_agent(toolkit)
    #     result = await agent.async_run(f"帮我看看这个文本是否符合规范：我爱中国")
    #     print("result -> ", result)

    #     result = await agent.async_run(f"帮我看看这个文本是否符合规范：sjsjsj")
    #     print("result -> ", result)

    # @pytest.mark.asyncio
    # async def test_plugin_image_moderation(self):
    #     url = "https://tool-image-moderation.aistudio-hub.baidu.com"
    #     toolkit = RemoteToolkit.from_url(url, version="v1.2", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

    #     file_manager = FileManager()

    #     file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Downloads/43.png")

    #     agent = self.get_agent(toolkit)
    #     result = await agent.async_run(f"帮我看看图片内容是否符合规范\n\n图片：[{file.id}]")
    #     print("result -> ", result)

    # @pytest.mark.asyncio
    # async def test_image_enhancement(self):
    #     url = "https://tool-img-enhance.aistudio-hub.baidu.com"
    #     toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    #     # toolkit = RemoteToolkit.from_openapi_file("openapi.larger.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

    #     file_manager = FileManager()

    #     file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Downloads/43.png")

    #     agent = self.get_agent(toolkit)
    #     result = await agent.async_run(f"请帮我将图片无损放大一下\n\n图片：[{file.id}]")
    #     content = await result.files[-1].file.read_contents()
    #     print(result)
    #     with open("sss.png", "wb") as f:
    #         f.write(content)

    #     assert len(result.files) == 2
    #     assert ".png" in result.files[0].file.filename

    #     print("result -> ", result)

    # @pytest.mark.asyncio
    # async def test_text_to_audio(self):
    #     url = "http://tool-texttospeech.sandbox-aistudio-hub.baidu.com"
    #     toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

    #     agent = self.get_agent(toolkit)
    #     result = await agent.async_run(f"帮我把这句话转化成语音：我爱中国")
    #     assert len(result.files) == 1
    #     # assert ".m3a" in result.files[0].file.filename
    #     print(result.files)
    #     file = result.files[0]

    @pytest.mark.asyncio
    async def test_humanseg(self):
       
        file_manager = FileManager()
        
        # url = "https://dfn9ed87r7138fi3.aistudio-hub.baidu.com" 
        url = 'http://tool-pp-human-v2.sandbox-aistudio-hub.baidu.com'   
        # 4ce50e3378f418d271c480c8ddfa818537071dbe    
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb", file_manager = file_manager)

        agent = self.get_agent(toolkit)
        
        file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Desktop/human_attr.jpg")
        result = await agent.async_run(f"帮我把这张图片里面的行人分离出来", files=[file])
        assert len(result.files) == 2
        file = result.files[0]
        breakpoint()

    @pytest.mark.asyncio
    async def test_ocr_structure(self):
       
        file_manager = FileManager()
        
        # url = "https://yfo319edw9s7d2t6.aistudio-hub.baidu.com"
        url = 'http://tool-pp-structure-v2.sandbox-aistudio-hub.baidu.com' 
        #4ce50e3378f418d271c480c8ddfa818537071dbe
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb", file_manager = file_manager)

        agent = self.get_agent(toolkit)

        file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Desktop/Unknown.png")
        result = await agent.async_run(f"帮我提取这个表格的内容，以markdown的形式输出", files=[file])
        assert len(result.files) == 1
        file = result.files[0]



    # @pytest.mark.asyncio
    # async def test_plugin_schema(self):
    #     url = "https://tool-highacc-ocr.aistudio-hub.baidu.com"
    #     toolkit = RemoteToolkit.from_url(url, version="v1.3", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

    #     file_manager = FileManager()

    #     file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Desktop/test_ocr.png")

    #     agent = self.get_agent(toolkit)
    #     result = await agent.async_run(f"帮我抽取一下图片里面的内容\n\n图片：[{file.id}]")
    #     print("result -> ", result)
