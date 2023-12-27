import io

import pytest
from PIL import Image

from erniebot_agent.tools.ImageGenerateTool import ImageGenerationTool


@pytest.mark.asyncio
async def test_image_generation_tool():
    # 创建 ImageGenerationTool 实例
    image_gen_tool = ImageGenerationTool()

    byte_str = await image_gen_tool(prompt="test_prompt", width=512, height=512, image_num=1)
    Image.open(io.BytesIO(byte_str)).show()

    assert isinstance(byte_str, bytes)
    assert len(byte_str) > 0
