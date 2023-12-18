from __future__ import annotations

import os


os.environ["EB_MAX_RETRIES"] = "100"
os.environ["EB_BASE_URL"] = "http://10.154.81.14:8868/ernie-foundry/v1"

import erniebot

erniebot.api_type = 'aistudio'
erniebot.access_token = '7d94e511182b340758dd9835de044a7865b736b2'
# erniebot.access_token = "1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb"

import pytest
import unittest

from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.tools.base import RemoteTool
from erniebot_agent.tools.remote_toolkit import RemoteToolkit
from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.tools.tool_manager import ToolManager
from erniebot_agent.memory import WholeMemory

class TestOCRRemotePlugin(unittest.IsolatedAsyncioTestCase):


    def get_agent(self, toolkit: RemoteToolkit):
        # llm = ERNIEBot(model="ernie-bot", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb", api_type = 'aistudio')
        # llm = ERNIEBot(model="ernie-bot-8k")
        llm = ERNIEBot(model="ernie-bot", api_type="custom")
        
        agent = FunctionalAgent(
            llm=llm,
            tools=ToolManager(tools=toolkit.get_tools()),
            memory=WholeMemory(),
        )
        return agent
        

    @pytest.mark.asyncio
    async def test_human_seg(self):
        # 人体分割
        # invalid param
        url = "http://tool-humanseg.sandbox-aistudio-hub.baidu.com"
        # toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        toolkit = RemoteToolkit.from_openapi_file("openapi.humanseg.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我把这张图片进行人像分割：{file.id}")
        print(result)
        # import pdb; pdb.set_trace()

    @pytest.mark.asyncio
    async def test_doc_rm_bnd(self):
        # 底纹删除
        # 问题：response 中没有定义数据格式
        url = "http://tool-rm-doc-img-bnd.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_aistudio("rm-doc-img-bnd")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.rm-doc-img-bnd.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        # file = await file_manager.create_file_from_path("./img-rm-bnd.png")
        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)

        # tool: RemoteTool = agent._tool_manager.get_tool("rm-doc-img-bnd/v2.0/rm_doc_img_bkd")
        # tool.response_prompt = "请将文本润色成 markdown 的格式"

        result = await agent.async_run(f"请帮我把这张图片的底纹给删掉", files=[file])

        assert len(result.files) == 2
        file = result.files[1].file

        content = await file.read_contents()
        with open("sss.png", "wb") as f:
            f.write(content)

    @pytest.mark.asyncio
    async def test_dish_classify(self):
        # 菜品识别
        # invalid param
        url = "http://tool-dish-classify.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.rm-doc-img-bnd.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./yuxiangrousi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我把 这张照片中的菜品是什么：{file.id}")
        print(result)
        # import pdb; pdb.set_trace()

    @pytest.mark.asyncio
    async def test_rec_classify(self):
        # 车辆识别
        url = "http://tool-car-classify.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.rm-doc-img-bnd.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我看看 这张照片中 车是什么牌子的车：{file.id}")
        print(result)

    @pytest.mark.asyncio
    async def test_ocr_general(self):
        # 车辆识别
        url = "http://tool-ocr-general.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.rm-doc-img-bnd.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我把 这张照片中是个什么东西", files=[file])
        print(result)
        # import pdb; pdb.set_trace()

    @pytest.mark.asyncio
    async def test_shopping_receipt(self):
        # 车辆识别
        url = "http://tool-shopping-receipt.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.rm-doc-img-bnd.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./xiaopiao.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我把这张购物小票中有什么东西", files=[file])
        print(result)
    @pytest.mark.asyncio
    async def test_img_style_trans(self):
        # 车辆识别
        url = "http://tool-img-style-trans.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"帮我把这张图片转化为铅笔风格的图片", files=[file])
        print(result)

        file = result.files[1].file
        content = await file.read_contents()
        with open("sss.png", "wb") as f:
            f.write(content)
        
    @pytest.mark.asyncio
    async def test_person_animation(self):
        # 车辆识别
        url = "http://tool-person-animation.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./biyadi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"帮我把这张人像图片转化为动漫的图片", files=[file])
        print(result)

        file = result.files[1].file
        content = await file.read_contents()
        with open("sss.png", "wb") as f:
            f.write(content)

    @pytest.mark.asyncio
    async def test_hand_text_rec(self):
        # 车辆识别
        url = "http://tool-hand-text-rec.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./shouxiezi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"这张照片中的手写字是什么？", files=[file])
        print(result)

    @pytest.mark.asyncio
    async def test_doc_rm_hand_wrt(self):
        # 车辆识别
        url = "http://tool-doc-rm-hand-wrt.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./shouxiezi.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"这张照片中的手写字是什么？", files=[file])

        file = result.files[1].file
        content = await file.read_contents()
        with open("sss.png", "wb") as f:
            f.write(content)


# 文档去手写：http://tool-doc-rm-hand-wrt.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 手写文字识别：http://tool-hand-text-rec.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 人像动漫化：http://tool-person-animation.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 图像风格转换：http://tool-img-style-trans.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml

# async def main():
#     tester = TestOCRRemotePlugin()

#     await tester.test_doc_rm_bnd()


# import asyncio
# asyncio.run(main())

# 文档去底纹：http://tool-rm-doc-img-bnd.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 菜品识别：http://tool-dish-classify.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 车辆识别：http://tool-car-classify.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml

# todo:
# 通用物体和场景识别：http://tool-ocr-general.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 购物小票识别：http://tool-shopping-receipt.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml

# done:
# 文档去底纹：http://tool-rm-doc-img-bnd.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
# 车辆识别：http://tool-car-classify.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml

# fixMe:
# 菜品识别：http://tool-dish-classify.sandbox-aistudio-hub.baidu.com/.well-known/openapi.yaml
            
from __future__ import annotations

import os
import pytest
import unittest

from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.tools.base import RemoteToolkit
from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.tools.tool_manager import ToolManager
from erniebot_agent.memory import WholeMemory

import erniebot

erniebot.api_type = 'aistudio'
erniebot.access_token = '7d94e511182b340758dd9835de044a7865b736b2'


os.environ["EB_MAX_RETRIES"] = "100"
os.environ["EB_BASE_URL"] = "http://10.154.81.14:8868/ernie-foundry/v1"


class TestOCRRemotePlugin(unittest.IsolatedAsyncioTestCase):


    def get_agent(self, toolkit: RemoteToolkit):
        # llm = ERNIEBot(model="ernie-bot", access_token="7d109d14c26a3e0e5a01f841927c30331ad07e62", api_type = 'aistudio')
        # llm = ERNIEBot(model="ernie-bot-8k")
        llm = ERNIEBot(model="ernie-bot", api_type="custom")
        
        agent = FunctionalAgent(
            llm=llm,
            tools=ToolManager(tools=toolkit.get_tools()),
            memory=WholeMemory(),
        )
        return agent
        

    @pytest.mark.asyncio
    async def test_doc_analysis(self):
        url = "http://tool-doc-analysis.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.docx.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./开源与商业.pdf")


        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请帮我分析一下这个文档里面的内容：{file.id}")
        print(result)

    @pytest.mark.asyncio
    async def test_formula(self):
        url = "http://tool-formula.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.docx.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./math-formula.png")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"请抽取一下这张图片里面的公式：{file.id}")
        print(result)

    @pytest.mark.asyncio
    async def test_official_doc(self):
        url = "http://tool-official-doc-rec.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
        # toolkit = RemoteToolkit.from_openapi_file("openapi.docx.yaml", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        file_manager = FileManager()

        # file = await file_manager.create_file_from_path("./paddle.docx")
        file = await file_manager.create_file_from_path("./开源与商业.pdf")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"帮我识别一下这个 文件里面的内容 文件的内容：{file.id}")
        print(result)


    @pytest.mark.asyncio
    async def test_paddle_tts(self):
        url = "http://tool-12140.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        agent = self.get_agent(toolkit)
        result = await agent.async_run(f"帮我把：“我爱中国”转化成语音")

        print(result)

        assert len(result.files) == 1
        assert ".wav" in result.files[0].file.filename
        file = result.files[0].file

        url = "http://tool-asr.sandbox-aistudio-hub.baidu.com"

        content = await file.read_contents()
        with open("sss.wav", "wb") as f:
            f.write(content)
        print("Done")

    @pytest.mark.asyncio
    async def test_landmark(self):
        url = "http://tool-landmark-rec.sandbox-aistudio-hub.baidu.com"
        toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")

        agent = self.get_agent(toolkit)
        file_manager = FileManager()

        file = await file_manager.create_file_from_path("./shanghai-dongfangmingzhu.png")
        result = await agent.async_run(f"帮我识别一下图片中建筑物所在的位置，图片为：{file.id}")

        print(result)
        # import pdb; pdb.set_trace()