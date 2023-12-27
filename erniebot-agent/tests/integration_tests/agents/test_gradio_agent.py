import os

from erniebot_agent.agents.functional_agent import FunctionalAgent
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.file.file_manager import FileManager
from erniebot_agent.memory import WholeMemory
from erniebot_agent.tools import RemoteToolkit
from erniebot_agent.tools.mimic_imgtool import ImageSegmentTool
from erniebot_agent.tools.tool_manager import ToolManager


async def image_moderation():
    tools = []
    # url = "https://tool-image-moderation.aistudio-hub.baidu.com"
    # toolkit = RemoteToolkit.from_url(url, version="v1.2", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    # tools.extend(toolkit.get_tools())
    # url = "https://tool-highacc-ocr.aistudio-hub.baidu.com"
    # toolkit = RemoteToolkit.from_url(url, version="v1.3", access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    # tools.extend(toolkit.get_tools())
    # url = "https://tool-img-enhance.aistudio-hub.baidu.com"
    # toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    # tools.extend(toolkit.get_tools())
    # url = "http://tool-texttospeech.sandbox-aistudio-hub.baidu.com"
    # toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    # tools.extend(toolkit.get_tools())
    url = "http://tool-pp-structure-v2.sandbox-aistudio-hub.baidu.com"
    toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    tools.extend(toolkit.get_tools())
    # url = "https://dfn9ed87r7138fi3.aistudio-hub.baidu.com"
    # url = 'http://tool-pp-human-v2.sandbox-aistudio-hub.baidu.com'   
    # toolkit = RemoteToolkit.from_url(url, access_token="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb")
    # tools.extend(toolkit.get_tools())
    # url = "https://yfo319edw9s7d2t6.aistudio-hub.baidu.com"
    # toolkit = RemoteToolkit.from_url(url, access_token="4ce50e3378f418d271c480c8ddfa818537071dbe")
    # tools.extend(toolkit.get_tools())

    llm = ERNIEBot(
        model="ernie-bot", api_type="custom"
    )

    agent = FunctionalAgent(
        llm=llm,
        tools=ToolManager(tools=tools),
        memory=WholeMemory(),
    )

    # file_manager = FileManager()
    # file = await file_manager.create_file_from_path(r"/Users/tanzhehao/Downloads/43.png")
    # result = await agent.async_run(f"帮我看看图片内容是否符合规范\n\n图片：[{file.id}]")
    # print("result -> ", result)
    agent.launch_gradio_demo()


if __name__ == "__main__":
    import asyncio

    async def main():
        await image_moderation()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
