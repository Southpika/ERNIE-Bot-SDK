from __future__ import annotations

<<<<<<< HEAD
import logging

import pytest
from erniebot_agent.file_io.file_manager import FileManager
=======
import pytest

>>>>>>> upstream/develop
from erniebot_agent.tools.remote_toolkit import RemoteToolkit

from .base import RemoteToolTesting

<<<<<<< HEAD
logger = logging.getLogger(__name__)

=======
>>>>>>> upstream/develop

class TestRemoteTool(RemoteToolTesting):
    @pytest.mark.asyncio
    async def test_dish_classify(self):
        toolkit = RemoteToolkit.from_aistudio("dish-classify")

<<<<<<< HEAD
        file_manager = FileManager()

        file = await file_manager.create_file_from_path(
            self.download_file("https://paddlenlp.bj.bcebos.com/ebagent/ci/fixtures/remote-tools/dish.png")
        )
=======
        file = await self.file_manager.create_file_from_path(self.download_fixture_file("dish.png"))
>>>>>>> upstream/develop
        agent = self.get_agent(toolkit)

        result = await agent.async_run("这张照片中的菜品是什么", files=[file])
        self.assertEqual(len(result.files), 1)
<<<<<<< HEAD
        logger.info(result)
=======
        self.assertIn("蛋", result.text)
>>>>>>> upstream/develop
