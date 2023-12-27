import asyncio

from erniebot_agent.agents import FunctionAgent
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.file import GlobalFileManagerHandler
from erniebot_agent.memory.whole_memory import WholeMemory
from erniebot_agent.tools import RemoteToolkit


class CVToolkit:
    def __init__(self):
        API_URL = "http://10.21.226.150:8097"
        self.toolkit = RemoteToolkit.from_url(
            API_URL, access_token="7d109d14c26a3e0e5a01f841927c30331ad07e62"
        )
        self.tools = self.toolkit.get_tools()


llm = ERNIEBot(model="ernie-3.5", api_type="aistudio", access_token="<your-access-token>")
toolkit = CVToolkit()
memory = WholeMemory()
file_manager = get_file_manager()
agent = FunctionalAgent(llm=llm, tools=toolkit.tools, memory=memory, file_manager=file_manager)


async def run_agent():
    await GlobalFileManagerHandler().configure(access_token="<your-access-token>")

    llm = ERNIEBot(model="ernie-bot", api_type="aistudio", access_token="<your-access-token>")
    toolkit = CVToolkit()
    memory = WholeMemory()
    agent = FunctionAgent(llm=llm, tools=toolkit.tools, memory=memory)

    file_manager = await GlobalFileManagerHandler().get()
    seg_file = await file_manager.create_file_from_path(file_path="cityscapes_demo.png", file_type="local")
    clas_file = await file_manager.create_file_from_path(file_path="class_img.jpg", file_type="local")
    ocr_file = await file_manager.create_file_from_path(file_path="ch.png", file_type="local")
    agent_resp = await agent.run("这张图片中包含什么中文文字?", files=[ocr_file])  # 单张输入
    print("=" * 10 + "OCR返回结果" + "=" * 10 + "\n")
    print(agent_resp.text)
    print(agent_resp.annotations)
    print("\n" + "=" * 20 + "\n")
    agent_resp = await agent.run("请对第一张图片中的物体进行分类然后对第二张图片中的物体进行分割？", files=[clas_file, seg_file])  # 多张输入
    print("=" * 10 + "分类+分割返回结果" + "=" * 10 + "\n")
    print(agent_resp.text)
    print(agent_resp.annotations)
    print("\n" + "=" * 20 + "\n")
    agent_resp = await agent.run("请对上一张分割后的结果进行分类")  # 上一轮指代
    print("=" * 10 + "上一轮图片分割" + "=" * 10 + "\n")
    print(agent_resp.text)
    print(agent_resp.annotations)
    print("\n" + "=" * 20 + "\n")
    agent_resp = await agent.run("请帮我将这张中的汽车分割出来", files=[seg_file])
    print("=" * 10 + "分割返回结果" + "=" * 10 + "\n")
    print(agent_resp.text)
    print(agent_resp.annotations)
    print("\n" + "=" * 20 + "\n")


if __name__ == "__main__":
    # asyncio.run(run_agent())
    agent.launch_gradio_demo()  # gradio 还没加上文件上传等
