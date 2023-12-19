from __future__ import annotations

import asyncio
import io
import os
import unittest

from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.file_io.remote_file_clients.bos_file_client import BOSFileClient
from erniebot_agent.tools.base import RemoteToolkit
from PIL import Image

import erniebot

API_URL = "https://aistudio.baidu.com/bd-gpu-04/user/732872/7155718/api_serving/8080"

headers = {
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


class ImageGenerateTool(unittest.TestCase):
    def __init__(self) -> None:
        self.toolkit = RemoteToolkit.from_url(
            API_URL, access_token="7d109d14c26a3e0e5a01f841927c30331ad07e62"
        )
        remote_file_client = BOSFileClient(
            ak="8343f27745d74e6f97c99de824cd8866",
            sk="7270c84056034bd5a112b43f952aaf34",
            bucket_name="gdfdudu",
            prefix="erniebot-agent/",
        )
        self.file_manager = FileManager(remote_file_client=remote_file_client, auto_register=True)

    def __call__(self, query):
        async def test_text_to_image_func():
            tool_name = "textToImage"
            text_to_image_tool = self.toolkit.get_tool(tool_name)
            # prompt = "你是郭靖，走在古代中国临安市的街道上，街道繁忙，市场生动。周围是传统的中国建筑，人们穿着符合时代的服饰，忙碌地走来走去或交谈着。"
            # prompt = "You are Guo Jing, walking on the streets of Lin'an City in ancient China. The streets are busy and the markets are lively. Surrounded by traditional Chinese buildings, people dressed in period-appropriate clothing were busy walking around or talking."
            prompt = erniebot.ChatCompletion.create(
                model="ernie-bot-4", messages=[{"role": "user", "content": f"请翻译成英语:{query}"}]
            ).get_result()
            res = await text_to_image_tool(text=prompt)  # json error 补充

            remote_file = await self.file_manager.retrieve_remote_file(res["file_id"])
            byte_str = await remote_file.read_content()  # TODO: transfer to image

            all_files = os.listdir("/private/var/folders/gw/lbw__qt16dl3sdh_5cgv_jl00000gn/T/gradio/")
            num_png_files = 0
            for file in all_files:
                if file.endswith(".png"):
                    num_png_files += 1
            save_path = (
                f"/private/var/folders/gw/lbw__qt16dl3sdh_5cgv_jl00000gn/T/gradio/temp_{num_png_files+1}.png"
            )
            bytestr_to_png(byte_str, save_path)
            await remote_file.delete()

            self.assertTrue(res["message"] != "")
            self.assertTrue("失败" not in res["message"])
            return save_path

        return asyncio.run(test_text_to_image_func())


if __name__ == "__main__":
    # import requests

    # response = requests.get(API_URL + "/.well-known/openapi.yaml", headers=headers)
    # print(response.content.decode())

    img_tool = ImageGenerateTool()
    img_tool(
        "You are Guo Jing, walking on the streets of Lin'an City in ancient China. The streets are busy and the markets are lively. Surrounded by traditional Chinese buildings, people dressed in period-appropriate clothing were busy walking around or talking."
    )
