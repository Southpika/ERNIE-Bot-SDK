import asyncio
import os
import unittest

import pytest
from erniebot_agent.tools.browser_main import Browser_Manager
from erniebot_agent.tools.text2img import ImageGenerateTool

import erniebot

erniebot.api_type = "aistudio"
erniebot.access_token = os.getenv("EB_ACCESS_TOKEN")


class TestSearchTool(unittest.TestCase):
    # def test_search(self):
    #     browser = Browser_Manager(web_num=5)
    #     references = browser.search(search_type='search', query='孤注一掷怎么样')

    #     assert '参考文档 10' in references

    def test_schema(self):
        t2img_tool = ImageGenerateTool()
        function_call_schema = t2img_tool.function_call_schema()
        print(function_call_schema)

        self.assertEqual(function_call_schema["description"], "ImageGenerateTool用于根据用户的文字提示，生成图片。")
        self.assertIn("query", function_call_schema["parameters"]["properties"])

    # def test_news_search(self):
    #     browser = Browser_Manager(web_num=5)
    #     references = browser.search(search_type='news', query='帮我查一下今天的新闻')

    #     assert '参考文档 5' in references

    # @pytest.mark.asyncio
    # async def test_tool(self):
    #     search_tool = SearchTool()
    #     references = await search_tool(search_type='search', query='孤注一掷怎么样')
    #     print('referece', references)
    #     assert '参考文档 5' in references
