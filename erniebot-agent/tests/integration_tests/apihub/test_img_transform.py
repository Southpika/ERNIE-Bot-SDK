'''
Author: Southpika 513923576@qq.com
Date: 2023-12-20 17:32:24
LastEditors: Southpika 513923576@qq.com
LastEditTime: 2023-12-20 17:38:43
FilePath: /ERINE/ERNIE-Bot-SDK/erniebot-agent/tests/integration_tests/apihub/test_img_transform.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from __future__ import annotations

import pytest

from erniebot_agent.tools.remote_toolkit import RemoteToolkit

from .base import RemoteToolTesting


class TestRemoteTool(RemoteToolTesting):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.file = await self.file_manager.create_file_from_path(self.download_fixture_file("trans.png"))

    @pytest.mark.asyncio
    async def test_img_style_trans(self):
        toolkit = RemoteToolkit.from_aistudio("img-style-trans", file_manager=self.file_manager)

        agent = self.get_agent(toolkit)

        result = await agent.async_run("帮我把这个图片转换为卡通风格", files=[self.file])
        self.assertEqual(len(result.files), 2)

    @pytest.mark.asyncio
    async def test_person_animation(self):
        toolkit = RemoteToolkit.from_aistudio("person-animation", file_manager=self.file_manager)

        agent = self.get_agent(toolkit)

        result = await agent.async_run("帮我把这张人像图片转化为动漫的图片", files=[self.file])
        self.assertEqual(len(result.files), 2)
