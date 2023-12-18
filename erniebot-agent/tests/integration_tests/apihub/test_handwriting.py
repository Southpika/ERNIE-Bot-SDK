from __future__ import annotations

import asyncio

import pytest
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.tools.remote_toolkit import RemoteToolkit
from PIL import Image

from .base import RemoteToolTesting


class TestRemoteTool(RemoteToolTesting):
    def setUp(self) -> None:
        super().setUp()
        self.file_manager = FileManager()
        self.file = asyncio.run(
            self.file_manager.create_file_from_path(
                self.download_file(
                    "https://paddlenlp.bj.bcebos.com/ebagent/ci/fixtures/remote-tools/shouxiezi.png"
                )
            )
        )

    @pytest.mark.asyncio
    async def test_hand_text_rec(self):
        toolkit = RemoteToolkit.from_aistudio("hand-text-rec")

        agent = self.get_agent(toolkit)

        result = await agent.async_run("这张照片中的手写字是什么？", files=[self.file])
        self.assertEqual(len(result.files), 1)

    @pytest.mark.asyncio
    async def test_doc_rm_hand_wrt(self):
        toolkit = RemoteToolkit.from_aistudio("doc-rm-hand-wrt")

        agent = self.get_agent(toolkit)

        result = await agent.async_run("帮我把这张这张照片中的手写字的背景去除", files=[self.file])
        self.assertEqual(len(result.files), 2)
        Image.open(result.files[-1].file.path).show()
