"""
Author: Southpika 513923576@qq.com
Date: 2023-11-24 17:17:46
LastEditors: Southpika 513923576@qq.com
LastEditTime: 2023-11-27 17:31:08
FilePath: /ERINE/ERNIE-Bot-SDK/erniebot-agent/erniebot_agent/tools/img_main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""
from __future__ import annotations

import asyncio
import io
import unittest

from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.file_io.remote_file_clients.bos_file_client import BOSFileClient
from erniebot_agent.tools.base import RemoteToolkit
from PIL import Image

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


class TestCVToolKit(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_text_to_image(self):
        async def test_text_to_image_func():
            tool_name = "textToImage"
            text_to_image_tool = self.toolkit.get_tool(tool_name)
            # prompt = "你是郭靖，走在古代中国临安市的街道上，街道繁忙，市场生动。周围是传统的中国建筑，人们穿着符合时代的服饰，忙碌地走来走去或交谈着。"
            prompt = "You are Guo Jing, walking on the streets of Lin'an City in ancient China. The streets are busy and the markets are lively. Surrounded by traditional Chinese buildings, people dressed in period-appropriate clothing were busy walking around or talking."
            res = await text_to_image_tool(text=prompt)  # json error 补充

            remote_file = await self.file_manager.retrieve_remote_file(res["file_id"])
            byte_str = await remote_file.read_content()  # TODO: transfer to image
            bytestr_to_png(byte_str, "text_to_image.png")
            remote_file.delete()

            self.assertTrue(res["message"] != "")
            self.assertTrue("失败" not in res["message"])
            print(res)

        asyncio.run(test_text_to_image_func())


if __name__ == "__main__":
    import requests

    response = requests.get(API_URL + "/.well-known/openapi.yaml", headers=headers)
    print(response.content.decode())

    unittest.main()
