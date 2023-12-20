'''
Author: Southpika 513923576@qq.com
Date: 2023-12-20 17:32:24
LastEditors: Southpika 513923576@qq.com
LastEditTime: 2023-12-20 17:38:23
FilePath: /ERINE/ERNIE-Bot-SDK/erniebot-agent/tests/integration_tests/apihub/test_doc_analysis.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from __future__ import annotations

import asyncio

import pytest
from erniebot_agent.tools.remote_toolkit import RemoteToolkit

from .base import RemoteToolTesting


class TestRemoteTool(RemoteToolTesting):
    def setUp(self) -> None:
        super().setUp()
        self.file = asyncio.run(
            self.file_manager.create_file_from_path(self.download_fixture_file("城市管理执法办法.pdf"))
        )

    @pytest.mark.asyncio
    async def test_doc_analysis(self):
        toolkit = RemoteToolkit.from_aistudio("doc-analysis")

        agent = self.get_agent(toolkit)

        result = await agent.async_run("请帮我分析一下这个文档里面的内容：", files=[self.file])
        self.assertEqual(len(result.files), 1)
        self.assertIn("城市管理执法办法", result.text)

    async def test_official_doc(self):
        toolkit = RemoteToolkit.from_aistudio("official-doc-rec")

        agent = self.get_agent(toolkit)

        result = await agent.async_run("帮我识别一下这个文件里面的内容：", files=[self.file])
        self.assertEqual(len(result.files), 1)
        self.assertIn("城市管理执法办法", result.text)
