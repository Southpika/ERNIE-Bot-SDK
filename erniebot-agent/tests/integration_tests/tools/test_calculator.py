'''
Author: Southpika 513923576@qq.com
Date: 2023-11-19 16:48:16
LastEditors: Southpika 513923576@qq.com
LastEditTime: 2023-12-04 19:02:25
FilePath: /ERINE/ERNIE-Bot-SDK/erniebot-agent/tests/integration_tests/tools/test_calculator.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from __future__ import annotations

import asyncio
import json
import os
import unittest

from erniebot_agent.tools.calculator_tool import CalculatorTool

import erniebot

erniebot.api_type = "aistudio"
erniebot.access_token = os.environ["EB_ACCESS_TOKEN"]


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = CalculatorTool()

    def run_query(self, query):
        response = erniebot.ChatCompletion.create(
            model="ernie-bot",
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            functions=[self.tool.function_call_schema()],
            stream=False,
        )
        result = response.get_result()
        if isinstance(result, str):
            return result

        assert result["name"] == "CalculatorTool"
        arguments = json.loads(result["arguments"])
        result = asyncio.run(self.tool(**arguments))
        return result

    def test_add(self):
        result = self.run_query("3 加四等于多少")
        self.assertEqual(result["formula_result"], 7)

    def test_complex_formula(self):
        result = self.run_query("3乘以五 再加10等于多少")
        self.assertEqual(result["formula_result"], 25)
